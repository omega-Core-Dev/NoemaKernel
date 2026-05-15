from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem


def main() -> None:
    contexts = [
        ContextItem(
            context_id="ctx_001",
            content=(
                "Eu almejo uma LLM de convivio. Nao quero apenas uma ferramenta que responde. "
                "Quero que ela perceba frases pequenas e instigue reflexao sem ser intrusiva."
            ),
        ),
        ContextItem(
            context_id="ctx_002",
            content=(
                "O Bankmap deve tratar muitos contextos em uma unica inferencia. "
                "Depois a saida precisa voltar separada em resposta, memoria, auditoria e noemas."
            ),
        ),
        ContextItem(
            context_id="ctx_003",
            content=(
                "O insight veio da leitura regressiva: o final de um livro pode ser o comeco "
                "para quem quer compreender a estrutura. Frases curtas podem carregar o contexto inteiro."
            ),
        ),
        ContextItem(
            context_id="ctx_004",
            content=(
                "Reducao de tokens so importa se preservar o sentido. "
                "Nao basta cortar firula; e preciso medir carga contextual e ambiguidade fertil."
            ),
        ),
    ]

    objective = "Prototipar Bankmap para reduzir tokens preservando contexto e output separado."
    engine = BankmapEngine()
    packet = engine.build_packet(contexts, objective)

    print("=== INFERENCE PACKET ===")
    print(packet.to_json())
    print("\n=== SIMULATED MULTI-FLOW OUTPUT ===")
    print(engine.simulate_output_json(packet))


if __name__ == "__main__":
    main()
