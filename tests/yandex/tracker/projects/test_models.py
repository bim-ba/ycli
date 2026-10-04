"""Model parsing for Tracker projects: the doc reply and the request bodies."""

from ycli.yandex.tracker.projects.models import Project, ProjectCreate, ProjectUpdate


def test_project_parses_the_doc_sample():
    project = Project.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/projects/9",
            "id": "9",
            "version": 1,
            "key": "Project",
            "name": "Project",
            "description": "My project",
            "lead": {"id": "11", "display": "Ann", "cloudUid": "ajep", "passportUid": 11},
            "status": "launched",
            "startDate": "2020-11-16",
            "endDate": "2020-12-16",
            "queues": [{"key": "TEST"}],
        }
    )
    assert (project.id, project.version, project.status) == ("9", 1, "launched")
    assert project.lead is not None and project.lead.display == "Ann"
    assert (project.start_date, project.end_date) == ("2020-11-16", "2020-12-16")
    assert project.queues == [{"key": "TEST"}]


def test_project_from_a_fresh_organization_has_no_lead_or_dates():
    project = Project.model_validate({"id": "1", "version": 2, "key": "K", "status": "draft"})
    assert project.lead is None and project.start_date is None and project.queues is None


def test_request_bodies_use_api_names_and_drop_unset_fields():
    created = ProjectCreate(
        name="N", queues="Q", status="DRAFT", start_date="2026-01-01"
    ).model_dump(by_alias=True, exclude_none=True, mode="json")
    assert created == {"name": "N", "queues": "Q", "status": "DRAFT", "startDate": "2026-01-01"}
    assert ProjectUpdate(queues="Q", end_date="2026-02-02").model_dump(
        by_alias=True, exclude_none=True
    ) == {"queues": "Q", "endDate": "2026-02-02"}
    for model in (ProjectCreate, ProjectUpdate, Project):
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
