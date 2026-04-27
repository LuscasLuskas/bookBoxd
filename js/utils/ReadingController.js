export class ReadingController {
    constructor(totalPaginas, totalCapitulos, diasParaConcluir = 30) {
        this.totalPaginas = totalPaginas;
        this.totalCapitulos = totalCapitulos;
        
        this.prazoDias = diasParaConcluir;
        this.prazoSemanas = Math.ceil(diasParaConcluir / 7); // Geralmente 4 semanas para um mês
        
        // Estado inicial padrão
        this.modoMedida = 'paginas'; // 'paginas' ou 'capitulos'
        this.modoFrequencia = 'diario'; // 'diario' ou 'semanal'
        
        this.unidadesConcluidas = 0;
    }

    // Atualiza as preferências do utilizador
    atualizarPreferencias(medida, frequencia) {
        this.modoMedida = medida;
        this.modoFrequencia = frequencia;
    }

    // Calcula quanto ler por ciclo para terminar no prazo
    calcularMetaAtual() {
        const total = this.modoMedida === 'paginas' ? this.totalPaginas : this.totalCapitulos;
        const divisor = this.modoFrequencia === 'diario' ? this.prazoDias : this.prazoSemanas;
        
        // Usamos Math.ceil para arredondar para cima (ex: 10.2 páginas vira 11) para garantir que o livro acaba no prazo
        return Math.ceil(total / divisor); 
    }

    // Retorna o texto formatado para a interface
    obterTextoMeta() {
        const meta = this.calcularMetaAtual();
        const rotuloMedida = this.modoMedida === 'paginas' ? 'Páginas' : 'Capítulos';
        const rotuloFrequencia = this.modoFrequencia === 'diario' ? 'por dia' : 'por semana';
        
        return `Meta: ${meta} ${rotuloMedida} ${rotuloFrequencia}`;
    }

    // Regista o progresso
    registrarLeitura() {
        const meta = this.calcularMetaAtual();
        const total = this.modoMedida === 'paginas' ? this.totalPaginas : this.totalCapitulos;
        
        this.unidadesConcluidas += meta;
        if (this.unidadesConcluidas > total) {
            this.unidadesConcluidas = total;
        }
    }

    // Calcula a percentagem para a barra de progresso
    calcularProgressoPercentual() {
        const total = this.modoMedida === 'paginas' ? this.totalPaginas : this.totalCapitulos;
        return (this.unidadesConcluidas / total) * 100;
    }
}