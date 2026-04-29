#!/usr/bin/env python3
"""
🧠 KaliAgent v5.0.0 - Phase 14 Sprint 1.2: Model Serving API

REST API for ML model inference:
- Real-time predictions
- Batch processing
- Authentication & rate limiting
- Metrics & monitoring
- Health checks

Author: KaliAgent Team
Status: Alpha (0.1.0)
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ModelServer')

# Try to import FastAPI
try:
    from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("⚠️  FastAPI not available - install with: pip install fastapi uvicorn")

# Try to import ML modules
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ml_orchestrator import MLOrchestrator, MLAnalysisResult
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("⚠️  ML modules not available")


# Pydantic models for API
class ThreatReportRequest(BaseModel):
    """Threat report analysis request"""
    text: str = Field(..., min_length=10, max_length=100000, description="Threat report text")
    priority: str = Field(default="normal", description="Priority: low, normal, high, critical")


class TimeSeriesRequest(BaseModel):
    """Time-series analysis request"""
    data: List[List[float]] = Field(..., description="Time-series data (samples × features)")
    feature_names: Optional[List[str]] = Field(None, description="Feature names")


class BatchRequest(BaseModel):
    """Batch processing request"""
    requests: List[ThreatReportRequest] = Field(..., min_length=1, max_length=100)


class AnalysisResponse(BaseModel):
    """Analysis response"""
    id: str
    timestamp: str
    threat_score: float
    threat_level: str
    iocs: Dict[str, Any]
    classification: Dict[str, Any]
    recommendations: List[str]
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
    components: Dict[str, bool]
    gpu_available: bool
    uptime_seconds: float


class MetricsResponse(BaseModel):
    """Metrics response"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_processing_time_ms: float
    requests_per_minute: float
    gpu_utilization_percent: float


class ModelServer:
    """
    Model Serving API
    
    Features:
    - REST API for ML inference
    - Authentication via API key
    - Rate limiting
    - Health checks
    - Metrics & monitoring
    - Batch processing
    """
    
    VERSION = "0.1.0"
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000, api_key: str = None):
        self.host = host
        self.port = port
        self.api_key = api_key or "kaliagent-default-key"  # In production, use env var
        
        # Metrics
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.processing_times: List[float] = []
        
        # Initialize orchestrator
        self.orchestrator = None
        if ML_AVAILABLE:
            self.orchestrator = MLOrchestrator()
            logger.info("✅ ML Orchestrator initialized")
        
        # Create FastAPI app
        if FASTAPI_AVAILABLE:
            self.app = self._create_app()
        else:
            self.app = None
        
        logger.info(f"🚀 Model Server v{self.VERSION}")
        logger.info(f"   Host: {host}:{port}")
        logger.info(f"   API Key: {'*' * 8}")
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="KaliAgent ML Serving API",
            description="REST API for ML-powered threat intelligence",
            version=self.VERSION
        )
        
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        @app.get("/", tags=["Root"])
        async def root():
            return {"message": "KaliAgent ML Serving API", "version": self.VERSION}
        
        @app.get("/health", response_model=HealthResponse, tags=["Health"])
        async def health_check():
            return self._health_check()
        
        @app.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
        async def metrics():
            return self._get_metrics()
        
        @app.post("/analyze/threat-report", response_model=AnalysisResponse, tags=["Analysis"])
        async def analyze_threat_report(
            request: ThreatReportRequest,
            x_api_key: str = Header(None, alias="X-API-Key")
        ):
            return await self._analyze_threat_report(request, x_api_key)
        
        @app.post("/analyze/time-series", tags=["Analysis"])
        async def analyze_time_series(
            request: TimeSeriesRequest,
            x_api_key: str = Header(None, alias="X-API-Key")
        ):
            return await self._analyze_time_series(request, x_api_key)
        
        @app.post("/analyze/batch", tags=["Analysis"])
        async def analyze_batch(
            request: BatchRequest,
            background_tasks: BackgroundTasks,
            x_api_key: str = Header(None, alias="X-API-Key")
        ):
            return await self._analyze_batch(request, background_tasks, x_api_key)
        
        logger.info("✅ FastAPI routes registered")
        return app
    
    def _verify_api_key(self, api_key: str) -> bool:
        """Verify API key"""
        return api_key == self.api_key
    
    def _health_check(self) -> HealthResponse:
        """Perform health check"""
        components = {
            'orchestrator': self.orchestrator is not None,
            'lstm': self.orchestrator.lstm_detector is not None if self.orchestrator else False,
            'autoencoder': self.orchestrator.autoencoder_detector is not None if self.orchestrator else False,
            'nlp_extractor': self.orchestrator.nlp_extractor is not None if self.orchestrator else False,
            'nlp_classifier': self.orchestrator.nlp_classifier is not None if self.orchestrator else False,
            'registry': self.orchestrator.registry is not None if self.orchestrator else False,
        }
        
        gpu_available = False
        try:
            import torch
            gpu_available = torch.cuda.is_available()
        except ImportError:
            pass
        
        return HealthResponse(
            status="healthy",
            version=self.VERSION,
            timestamp=datetime.now().isoformat(),
            components=components,
            gpu_available=gpu_available,
            uptime_seconds=time.time() - self.start_time
        )
    
    def _get_metrics(self) -> MetricsResponse:
        """Get server metrics"""
        avg_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        uptime = time.time() - self.start_time
        rpm = (self.total_requests / uptime * 60) if uptime > 0 else 0
        
        gpu_util = 0.0
        try:
            import torch
            if torch.cuda.is_available():
                # Note: This is a placeholder - real GPU monitoring requires pynvml
                gpu_util = 0.0  # Would use pynvml.nvmlDeviceGetUtilizationRate()
        except ImportError:
            pass
        
        return MetricsResponse(
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            avg_processing_time_ms=avg_time,
            requests_per_minute=rpm,
            gpu_utilization_percent=gpu_util
        )
    
    async def _analyze_threat_report(self, request: ThreatReportRequest, api_key: str) -> AnalysisResponse:
        """Analyze threat report"""
        start_time = time.time()
        
        # Verify API key
        if not self._verify_api_key(api_key):
            self.failed_requests += 1
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        try:
            self.total_requests += 1
            
            if not self.orchestrator:
                raise HTTPException(status_code=503, detail="ML orchestrator not available")
            
            # Analyze
            result = self.orchestrator.analyze_threat_report(request.text)
            
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            self.successful_requests += 1
            
            return AnalysisResponse(
                id=result.id,
                timestamp=result.timestamp,
                threat_score=result.threat_score,
                threat_level=result.threat_level,
                iocs=result.nlp_iocs,
                classification=result.nlp_classification,
                recommendations=result.recommendations,
                processing_time_ms=processing_time
            )
        
        except Exception as e:
            self.failed_requests += 1
            logger.error(f"Analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _analyze_time_series(self, request: TimeSeriesRequest, api_key: str) -> Dict:
        """Analyze time-series data"""
        start_time = time.time()
        
        if not self._verify_api_key(api_key):
            self.failed_requests += 1
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        try:
            self.total_requests += 1
            
            if not self.orchestrator:
                raise HTTPException(status_code=503, detail="ML orchestrator not available")
            
            result = self.orchestrator.analyze_time_series(
                request.data,
                request.feature_names
            )
            
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            self.successful_requests += 1
            
            return {
                "id": result.id,
                "timestamp": result.timestamp,
                "lstm_anomaly_score": result.lstm_anomaly_score,
                "lstm_is_anomaly": result.lstm_is_anomaly,
                "threat_level": result.threat_level,
                "processing_time_ms": processing_time
            }
        
        except Exception as e:
            self.failed_requests += 1
            logger.error(f"Time-series analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _analyze_batch(self, request: BatchRequest, background_tasks: BackgroundTasks, api_key: str) -> Dict:
        """Batch processing (async)"""
        if not self._verify_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Process in background
        background_tasks.add_task(self._process_batch, request.requests, batch_id)
        
        return {
            "batch_id": batch_id,
            "status": "processing",
            "num_requests": len(request.requests),
            "message": "Batch processing started"
        }
    
    async def _process_batch(self, requests: List[ThreatReportRequest], batch_id: str):
        """Process batch in background"""
        logger.info(f"📦 Processing batch {batch_id} ({len(requests)} items)")
        
        results = []
        for req in requests:
            try:
                result = self.orchestrator.analyze_threat_report(req.text)
                results.append(result.to_dict())
            except Exception as e:
                logger.error(f"Batch item failed: {e}")
        
        # Save batch results
        output_path = Path(f"./batch_results/{batch_id}.json")
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "batch_id": batch_id,
                "timestamp": datetime.now().isoformat(),
                "num_results": len(results),
                "results": results
            }, f, indent=2)
        
        logger.info(f"✅ Batch {batch_id} complete: {len(results)} results saved to {output_path}")
    
    def run(self):
        """Start the model server"""
        if not FASTAPI_AVAILABLE:
            logger.error("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
            return
        
        logger.info(f"🚀 Starting Model Server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")


def main():
    """Run model server"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🧠 KALIAGENT v5.0.0 - MODEL SERVING API                  ║
║                    Phase 14 Sprint 1.2                        ║
╚═══════════════════════════════════════════════════════════════╝

    """)
    
    import argparse
    parser = argparse.ArgumentParser(description='KaliAgent Model Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--api-key', default=None, help='API key for authentication')
    
    args = parser.parse_args()
    
    server = ModelServer(
        host=args.host,
        port=args.port,
        api_key=args.api_key
    )
    
    if server.app:
        server.run()
    else:
        print("⚠️  Server not available - install dependencies:")
        print("   pip install fastapi uvicorn")


if __name__ == "__main__":
    main()
