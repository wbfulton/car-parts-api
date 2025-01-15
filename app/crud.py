from typing import List

from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas

# GROUPS


def get_groups_nested(db: Session):
    groups = db.query(models.Group).all()

    parent_groups: models.Group = []
    for group in groups:
        if len(group.parents) == 0:
            parent_groups.append(group)

    return parent_groups


def get_groups_flat(db: Session, page_length: int = 10, token: int = 0):
    return db.query(models.Group).offset(token).limit(page_length).all()


def get_group(db: Session, id: int):
    return db.query(models.Group).get(id)


def wipe_groups(db: Session):
    db.query(models.Group).delete()
    db.commit()


def post_bulk_groups(db: Session, groups: List[schemas.CreateGroup]):
    for new_group in groups:
        # Add Group to DB if not already in
        group = db.query(models.Group).get(new_group.id)
        if group is None:
            group = models.Group(
                id=new_group.id,
                name=new_group.name,
                diagrams_url=new_group.diagrams_url,
            )
            db.add(group)

        # Update parent - child relations if necessary
        if new_group.parent_group_id is not None:
            parent_group = db.query(models.Group).get(new_group.parent_group_id)
            if group not in parent_group.children:
                parent_group.children.append(group)

        # Commit on each loop (not ACID) to speed up dev process
        db.commit()


# DIAGRAMS


def get_diagrams(db: Session):
    return db.query(models.Diagram).all()


def wipe_diagrams(db: Session):
    db.query(models.Diagram).delete()
    db.commit()


def post_bulk_diagrams(db: Session, diagrams: List[schemas.CreateDiagram]):
    for new_diagram in diagrams:
        # Add Diagram to DB if not already in
        diagram = db.query(models.Diagram).get(new_diagram.id)
        if diagram is None:
            diagram = models.Diagram(
                id=new_diagram.id,
                name=new_diagram.name,
                img_url=new_diagram.img_url,
            )
            db.add(diagram)

        # Update parent - child relations if necessary
        parent_group = db.query(models.Group).get(new_diagram.parent_group_id)
        if diagram not in parent_group.diagrams:
            parent_group.diagrams.append(diagram)

        # Commit on each loop (not ACID) to speed up dev process
        db.commit()


# PARTS


def get_parts(db: Session, page_length: int = 10, token: int = 0):
    return db.query(models.Part).offset(token).limit(page_length).all()


def wipe_parts(db: Session):
    db.query(models.Part).delete()
    db.commit()


def post_bulk_parts(db: Session, parts: List[schemas.CreatePart]):
    for new_part in parts:
        # Add Diagram to DB if not already in
        part = db.query(models.Part).filter(models.Part.number == new_part.number).all()
        if part is None or len(part) == 0:
            part = models.Part(
                number=new_part.number,
                # amount=part.amount,
                note=new_part.note,
                name=new_part.name,
                date_range=new_part.date_range,
            )
            db.add(part)
        else:
            part = part[0]

        # Update parent - child relations if necessary
        parent_diagram = db.query(models.Diagram).get(new_part.parent_diagram_id)
        if part not in parent_diagram.parts:
            parent_diagram.parts.append(part)

        # Commit on each loop (not ACID) to speed up dev process
        db.commit()


# SCRAPING


def get_urls(db: Session):
    pages = db.query(models.PartsSouqPageData).all()
    return pages


def get_group_url_html(db: Session, group_id: int) -> models.PartsSouqPageData | None:
    url = db.query(models.PartsSouqPageData).get(group_id)
    return url


def post_html_url(db: Session, new_page: schemas.CreatePartsSouqPageData):
    # Add Diagram to DB if not already in
    page = db.query(models.PartsSouqPageData).get(new_page.id)
    if page is None:
        page = models.PartsSouqPageData(
            id=new_page.id,
            url=new_page.url,
            html_string=new_page.html_string,
        )
        db.add(page)
    else:
        db.query(models.PartsSouqPageData).where(
            models.PartsSouqPageData.id == new_page.id
        ).update({models.PartsSouqPageData.html_string: new_page.html_string})

    # Commit on each loop (not ACID) to speed up dev process
    db.commit()
