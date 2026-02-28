import numpy as np
from sqlmodel import Session, select
from app.models import LabMetric
from app.database import engine
from app.models import PhishingMetric

# Report a failure event
def report_failure(simulation_id: str, step_number: int):
    with Session(engine) as session:
        statement = select(LabMetric).where(
            LabMetric.simulation_id == simulation_id,
            LabMetric.step_number == step_number
        )
        metric = session.exec(statement).first()

        if not metric:
            metric = LabMetric(
                simulation_id=simulation_id,
                step_number=step_number,
                fail_count=1
            )
        else:
            metric.fail_count += 1

        session.add(metric)
        session.commit()
        session.refresh(metric)
        return metric


# Apply Differential Privacy
def get_noisy_metrics():
    with Session(engine) as session:
        metrics = session.exec(select(LabMetric)).all()

        results = []
        for m in metrics:
            noisy_value = m.fail_count + np.random.laplace(0, 1)
            results.append({
                "simulation_id": m.simulation_id,
                "step_number": m.step_number,
                "fail_count_noisy": round(noisy_value, 2)
            })

        return results
def report_phishing(domain: str, is_suspicious: bool):
    with Session(engine) as session:
        statement = select(PhishingMetric).where(
            PhishingMetric.domain == domain
        )
        metric = session.exec(statement).first()

        if not metric:
            metric = PhishingMetric(domain=domain)

        if is_suspicious:
            metric.suspicious_count += 1
        else:
            metric.safe_count += 1

        session.add(metric)
        session.commit()
        session.refresh(metric)
        return metric


def get_noisy_phishing():
    with Session(engine) as session:
        metrics = session.exec(select(PhishingMetric)).all()

        results = []
        for m in metrics:
            results.append({
                "domain": m.domain,
                "suspicious_noisy": round(m.suspicious_count + np.random.laplace(0, 1), 2),
                "safe_noisy": round(m.safe_count + np.random.laplace(0, 1), 2)
            })

        return results