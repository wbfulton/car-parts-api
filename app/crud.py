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
        group = schemas.CreateGroup(**group)
        if group.id not in seen:
            seen.add(group.id)
            db.add(
                models.Group(
                    id=group.id,
                    name=group.name,
                    diagrams_url=group.diagrams_url,
                    is_root=group.is_root,
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
                    # group_id=diagram.group_id,
                )
            )
    db.commit()
