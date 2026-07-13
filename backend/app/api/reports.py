from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from backend.app.dependencies import get_report_workflow
from backend.app.models.schemas import AnalyzeSampleRequest, DiagnosticReportAnalysis
from backend.app.workflows.report_workflow import ReportWorkflow

router = APIRouter(tags=["reports"])


@router.post("/analyze-report", response_model=DiagnosticReportAnalysis)
async def analyze_report(
    file: UploadFile = File(...),
    lang: str = Query("en", description="Target output language: en, hi, es, te"),
    workflow: ReportWorkflow = Depends(get_report_workflow),
):
    try:
        return workflow.analyze_upload(file, lang)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(exc)}")


@router.post("/analyze-sample", response_model=DiagnosticReportAnalysis)
async def analyze_sample(
    request: AnalyzeSampleRequest,
    workflow: ReportWorkflow = Depends(get_report_workflow),
):
    try:
        return workflow.analyze_sample(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Sample report analysis error: {str(exc)}")


@router.post("/train-knowledge")
async def train_knowledge(workflow: ReportWorkflow = Depends(get_report_workflow)):
    try:
        return workflow.train_knowledge()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Knowledge training failed: {str(exc)}")


@router.post("/upload-guideline")
async def upload_guideline(
    file: UploadFile = File(...),
    workflow: ReportWorkflow = Depends(get_report_workflow),
):
    try:
        return workflow.upload_guideline(file)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process and index uploaded guideline: {str(exc)}")


@router.get("/benchmarks")
def get_benchmarks_metrics(workflow: ReportWorkflow = Depends(get_report_workflow)):
    return workflow.get_benchmarks()


@router.get("/knowledge-graph")
def get_knowledge_relations(workflow: ReportWorkflow = Depends(get_report_workflow)):
    return workflow.get_knowledge_graph()
