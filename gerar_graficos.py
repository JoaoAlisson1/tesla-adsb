import matplotlib.pyplot as plt
import pandas as pd


def gerar_graficos_tcc(csv_path: str = "dataset_experimentos_tesla.csv"):
    df = pd.read_csv(csv_path)

    plt.figure(figsize=(9, 5))
    ct = pd.crosstab(df["cenario"], df["status_tesla"], normalize="index") * 100

    ax = ct.plot(kind="bar", stacked=True, figsize=(9, 5), colormap="tab10")
    plt.title("Desempenho do Protocolo TESLA sob Níveis Crescentes de Perda no Rádio", fontsize=12)
    plt.xlabel("Cenário de Transmissão", fontsize=10)
    plt.ylabel("Percentual das Mensagens (%)", fontsize=10)
    plt.legend(title="Status TESLA", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("grafico_status_por_cenario.png", dpi=300)
    print("✓ Figura salva: grafico_status_por_cenario.png")
    plt.close()

    df_recebidos = df[df["status_tesla"] != "PERDIDO"].copy()

    plt.figure(figsize=(8, 4.5))
    for cenario in df_recebidos["cenario"].unique():
        sub_df = df_recebidos[df_recebidos["cenario"] == cenario]
        plt.hist(sub_df["latencia_canal"] * 1000, bins=15, alpha=0.5, label=cenario)

    plt.title("Distribuição da Latência do Canal de Rádio (ms)", fontsize=12)
    plt.xlabel("Latência Medida (ms)", fontsize=10)
    plt.ylabel("Quantidade de Pacotes", fontsize=10)
    plt.legend(title="Cenário")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("grafico_distribuicao_latencia.png", dpi=300)
    print("✓ Figura salva: grafico_distribuicao_latencia.png")
    plt.close()


if __name__ == "__main__":
    gerar_graficos_tcc()