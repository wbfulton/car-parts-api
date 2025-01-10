from typing import List

from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas

# GROUPS


def get_groups_nested(db: Session):
    all_groups = db.query(models.Group).all()
    cleaned_groups: List[models.Group] = []
    # ORM will every group flat, and nested.
    # We must clean this to be just nested
    for group in all_groups:
        if group.parent_group_id is None:
            cleaned_groups.append(group)
    return cleaned_groups


def get_groups_flat(db: Session, page_length: int = 10, token: int = 0):
    return db.query(models.Group).offset(token).limit(page_length).all()


def get_group(db: Session, id: int):
    return db.query(models.Group).get(id)


def wipe_groups(db: Session):
    db.query(models.Group).delete()
    db.commit()


def post_bulk_groups(db: Session, groups: List[schemas.CreateGroup]):
    seen = set()
    for group in groups:
        if group.id not in seen:
            seen.add(group.id)
            db.add(
                models.Group(
                    id=group.id,
                    name=group.name,
                    diagrams_url=group.diagrams_url,
                    parent_group_id=group.parent_group_id,
                )
            )
    db.commit()


# DIAGRAMS


def get_diagrams(db: Session):
    return db.query(models.Diagram).all()


def wipe_diagrams(db: Session):
    db.query(models.Diagram).delete()
    db.commit()


def post_bulk_diagrams(db: Session, diagrams: List[schemas.CreateDiagram]):
    seen = set()
    for diagram in diagrams:
        if diagram.id not in seen:
            seen.add(diagram.id)
            db.add(
                models.Diagram(
                    id=diagram.id,
                    name=diagram.name,
                    img_url=diagram.img_url,
                    parent_group_id=diagram.parent_group_id,
                )
            )
    db.commit()


# PARTS


def get_parts(db: Session, page_length: int = 10, token: int = 0):
    return db.query(models.Part).offset(token).limit(page_length).all()


def wipe_parts(db: Session):
    db.query(models.Part).delete()
    db.commit()


def post_bulk_parts(db: Session, parts: List[schemas.CreatePart]):
    seen = set()
    for part in parts:
        if part.id not in seen:
            seen.add(part.id)
            db.add(
                models.Part(
                    id=part.id,
                    parent_diagram_id=part.parent_diagram_id,
                    number=part.number,
                    amount=part.amount,
                    note=part.note,
                    name=part.name,
                    date_range=part.date_range,
                )
            )
    db.commit()
