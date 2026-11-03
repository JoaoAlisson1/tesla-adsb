import pandas as pd

def salvar_dataset_simulacao(historico_eventos: list[dict], filepath: str = "dados_simulacao.csv"):

    df = pd.DataFrame(historico_eventos)
    df.to_csv(filepath, index=False)
    print(f"✓ Dataset salvo com sucesso em: {filepath}")