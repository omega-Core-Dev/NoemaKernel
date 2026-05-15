from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel.validation import parse_json_output, validate_multiflow_output


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python .\\examples\\validate_output.py caminho\\resposta.json")
        raise SystemExit(2)

    path = Path(sys.argv[1])
    parsed, errors = parse_json_output(path.read_text(encoding="utf-8"))
    if errors:
        print({"is_valid": False, "errors": errors})
        raise SystemExit(1)

    print(validate_multiflow_output(parsed))


if __name__ == "__main__":
    main()
