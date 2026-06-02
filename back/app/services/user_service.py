import io
import os
import uuid

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.models.user import Role, User
from app.repositories.book_club_repository import BookClubRepository
from app.repositories.book_repository import BookRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.user_book_repository import UserBookRepository
from app.repositories.user_repository import UserRepository
from app.core.config import settings
from app.schemas.user import UserUpdate

AVATAR_DIR = "uploads/avatars"
MAX_AVATAR_BYTES = 5 * 1024 * 1024
# Map of Pillow-detected image formats to safe extensions. Driven by what the
# raw bytes actually are, not by the client-supplied Content-Type.
ALLOWED_AVATAR_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "GIF": ".gif",
}


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.club_repo = BookClubRepository(db)
        self.membership_repo = MembershipRepository(db)
        self.book_repo = BookRepository(db)
        self.user_book_repo = UserBookRepository(db)

    def get_profile(self, user: User) -> User:
        return user

    def get_public_profile(self, viewer: User, target_id: str) -> User:
        """Profile of another user, gated by the shared-club access rule."""
        from app.core.access import assert_can_view_user

        return assert_can_view_user(self.db, viewer, target_id)

    def update_profile(self, user: User, data: UserUpdate) -> User:
        fields = data.model_dump(exclude_unset=True)

        if "name" in fields and fields["name"]:
            user.name = fields["name"].strip()

        if "bio" in fields:
            bio = fields["bio"]
            user.bio = bio.strip() if bio and bio.strip() else None

        if "favorite_book_id" in fields:
            book_id = fields["favorite_book_id"]
            if book_id and not self.book_repo.get_by_id(book_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Livro favorito não encontrado",
                )
            user.favorite_book_id = book_id

        return self.user_repo.save(user)

    def update_avatar(self, user: User, file: UploadFile) -> User:
        # Read up to MAX+1 so we can reject oversized uploads without
        # ever materializing more than the allowed size in memory.
        contents = file.file.read(MAX_AVATAR_BYTES + 1)
        if len(contents) > MAX_AVATAR_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Imagem muito grande (máximo 5MB).",
            )

        # Verify the bytes are a real image. verify() reads headers only and
        # consumes the stream, so reopen on a fresh buffer for the extension.
        try:
            Image.open(io.BytesIO(contents)).verify()
            image_format = Image.open(io.BytesIO(contents)).format
        except (UnidentifiedImageError, OSError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo não é uma imagem válida.",
            )

        ext = ALLOWED_AVATAR_FORMATS.get(image_format or "")
        if not ext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato inválido. Use JPG, PNG, WEBP ou GIF.",
            )

        filename = f"{user.id}_{uuid.uuid4().hex[:8]}{ext}"

        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            from supabase import create_client
            sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            if user.avatar_url and "/storage/v1/object/public/avatars/" in user.avatar_url:
                old_path = user.avatar_url.split("/storage/v1/object/public/avatars/")[-1]
                sb.storage.from_("avatars").remove([old_path])

            mime = {".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}.get(ext, "image/jpeg")
            sb.storage.from_("avatars").upload(filename, contents, {"content-type": mime, "upsert": "true"})
            user.avatar_url = sb.storage.from_("avatars").get_public_url(filename)
        else:
            os.makedirs(AVATAR_DIR, exist_ok=True)
            with open(os.path.join(AVATAR_DIR, filename), "wb") as out:
                out.write(contents)
            previous = user.avatar_url
            user.avatar_url = f"/uploads/avatars/{filename}"
            if previous and previous.startswith("/uploads/avatars/"):
                try:
                    os.remove(previous.lstrip("/"))
                except OSError:
                    pass

        return self.user_repo.save(user)

    def delete_account(self, user: User, actor: User) -> None:
        if actor.role != Role.MASTER and actor.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para deletar este usuário",
            )
        self._delete_user_transactional(user)

    def _delete_user_transactional(self, user: User) -> None:
        clubs_owned = self.club_repo.get_clubs_owned_by(user.id)
        for club in clubs_owned:
            oldest_member = self.club_repo.get_oldest_active_member(
                club.id, exclude_user_id=user.id
            )
            if oldest_member:
                club.owner_id = oldest_member.user_id
            else:
                self.db.delete(club)

        self.db.flush()

        self.membership_repo.delete_by_user(user.id)
        self.user_book_repo.delete_by_user(user.id)
        self.book_repo.nullify_created_by(user.id, user.name)

        self.db.delete(user)
        self.db.flush()
