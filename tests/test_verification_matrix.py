import json
from importlib import import_module
from pathlib import Path


def test_verification_matrix_paths_exist_and_are_objective():
    repo = Path(__file__).resolve().parents[1]
    matrix_path = repo / "docs" / "verification_matrix_v1.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    assert matrix["version"] == "v1"
    assert matrix["items"]

    for item in matrix["items"]:
        assert item["id"]
        for key in ("code_modules", "tests", "evidence_artifacts"):
            assert item[key], f"{item['id']} missing {key}"
            for rel_path in item[key]:
                assert (repo / rel_path).exists(), f"{item['id']} missing referenced path: {rel_path}"

        for rel_path in item["code_modules"]:
            if not rel_path.endswith(".py"):
                continue
            module_name = rel_path.replace("/", ".").removesuffix(".py")
            import_module(module_name)
