import api from './client';
import type { Membership, MembershipListResponse, MembershipStatus } from '../types';

export const joinClub = async (clubId: string): Promise<Membership> => {
  const res = await api.post<Membership>(`/clubs/${clubId}/join`);
  return res.data;
};

export const leaveClub = async (clubId: string): Promise<Membership> => {
  const res = await api.post<Membership>(`/clubs/${clubId}/leave`);
  return res.data;
};

export const listMembers = async (
  clubId: string,
  status?: MembershipStatus
): Promise<MembershipListResponse> => {
  const res = await api.get<MembershipListResponse>(`/clubs/${clubId}/members`, {
    params: status ? { status } : undefined,
  });
  return res.data;
};

export const approveMember = async (
  clubId: string,
  userId: string
): Promise<Membership> => {
  const res = await api.post<Membership>(`/clubs/${clubId}/members/${userId}/approve`);
  return res.data;
};

export const rejectMember = async (
  clubId: string,
  userId: string
): Promise<Membership> => {
  const res = await api.post<Membership>(`/clubs/${clubId}/members/${userId}/reject`);
  return res.data;
};

export const banMember = async (
  clubId: string,
  userId: string
): Promise<Membership> => {
  const res = await api.post<Membership>(`/clubs/${clubId}/members/${userId}/ban`);
  return res.data;
};

export const kickMember = async (
  clubId: string,
  userId: string,
  kickedUntil: string
): Promise<Membership> => {
  const res = await api.post<Membership>(`/clubs/${clubId}/members/${userId}/kick`, {
    kicked_until: kickedUntil,
  });
  return res.data;
};
