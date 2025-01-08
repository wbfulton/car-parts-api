from typing import List

from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas

# GROUPS


def get_groups(db: Session):
    return db.query(models.Group).all()


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
                    sub_groups=group.sub_groups,
                    parent_group_id=group.parent_group_id,
                    diagrams=group.diagrams,
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
                    parts=diagram.parts,
                )
            )
    db.commit()


# DIAGRAMS


def get_parts(db: Session):
    return db.query(models.Part).all()


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
