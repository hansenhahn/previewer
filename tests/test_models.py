from infra.models import Project


def test_project_columns():
    columns = set(Project.__table__.columns.keys())
    assert {
        "id",
        "owner_id",
        "name",
        "encoding",
        "created_at",
        "updated_at",
    } <= columns


def test_project_unique_constraint_by_owner_and_name():
    names = {constraint.name for constraint in Project.__table__.constraints}
    assert "uq_projects_owner_name" in names
