from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Job
from ..schemas import JobCreate, JobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, session: Session = Depends(get_session)) -> Job:
    job = Job(**payload.model_dump())
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.get("/", response_model=list[JobRead])
def list_jobs(session: Session = Depends(get_session)) -> list[Job]:
    jobs = session.exec(select(Job)).all()
    return jobs


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, session: Session = Depends(get_session)) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
