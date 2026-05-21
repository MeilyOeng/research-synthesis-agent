import { useState, useRef, useCallback, useEffect } from 'react';
import './R_Sidebar.css';

const sources = [
  { id: 1, title: 'Overcoming Catastrophic Forgetting in Neural Networks', authors: 'Kirkpatrick et al., Proceedings of NAS, 2017', score: 96 },
  { id: 2, title: 'A Comprehensive, Application-Oriented Study of Catastrophic Forgetting in DNNs', authors: 'Rebuffi et al., IEEE TPAMI, 2017', score: 95 },
  { id: 3, title: 'iCaRL: Incremental Classifier and Representation Learning', authors: 'Rebuffi et al., CVPR, 2017', score: 94 },
  { id: 4, title: 'Gradient Episodic Memory for Continual Learning', authors: 'Lopez-Paz & Ranzato, NeurIPS, 2017', score: 92 },
  { id: 5, title: 'A Comprehensive, Application-Oriented Study of Catastrophic Forgetting in DNNs', authors: 'Rebuffi et al., IEEE TPAMI, 2017', score: 95 },
  { id: 6, title: 'iCaRL: Incremental Classifier and Representation Learning', authors: 'Rebuffi et al., CVPR, 2017', score: 94 },
  { id: 7, title: 'Gradient Episodic Memory for Continual Learning', authors: 'Lopez-Paz & Ranzato, NeurIPS, 2017', score: 92 },
  { id: 8, title: 'Continual Learning with Deep Generative Replay', authors: 'Shin et al., NeurIPS, 2017', score: 91 },
];

const qualityMetrics = [
  { label: 'Source Quality', value: 0.07 },
  { label: 'Coverage', value: 0.82 },
  { label: 'Consistency', value: 0.79 },
  { label: 'Recency', value: 0.85 },
];

const MIN_WIDTH = 260;
const MAX_WIDTH = 520;

const ScoreBar = ({ value }) => (
  <div className="score-bar-track">
    <div className="score-bar-fill" style={{ width: `${value * 100}%` }} />
  </div>
);

const R_Sidebar = () => {
  const [width, setWidth] = useState(320);
  const [showAllSources, setShowAllSources] = useState(false);
  const dragging = useRef(false);
  const startX = useRef(0);
  const startW = useRef(0);
  const sidebarRef = useRef(null);

  const overallConfidence = (qualityMetrics.reduce((s, m) => s + m.value, 0) / qualityMetrics.length).toFixed(2);

  const onMouseDown = useCallback((e) => {
    dragging.current = true;
    startX.current = e.clientX;
    startW.current = width;
    document.body.style.cursor = 'ew-resize';
    document.body.style.userSelect = 'none';
  }, [width]);

  useEffect(() => {
    const onMouseMove = (e) => {
      if (!dragging.current) return;
      const delta = startX.current - e.clientX;
      const newW = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, startW.current + delta));
      setWidth(newW);
    };
    const onMouseUp = () => {
      dragging.current = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, []);

  const visibleSources = showAllSources ? sources : sources.slice(0, 5);

  return (
    <div ref={sidebarRef} className="rsidebar" style={{ width }}>
      <div className="rsidebar-resize-handle" onMouseDown={onMouseDown} title="Drag to resize">
        <div className="rsidebar-resize-dots" />
      </div>

      <div className="rsidebar-scroll">
        <div className="rsidebar-card">
          <div className="rsidebar-card-header">
            <span className="rsidebar-card-title">Top Sources</span>
            <span className="rsidebar-source-count">({sources.length})</span>
            <button className="rsidebar-view-all" onClick={() => setShowAllSources(v => !v)}>
              {showAllSources ? 'Show less' : 'View all →'}
            </button>
          </div>

          <ol className="rsidebar-sources">
            {visibleSources.map((s) => (
              <li key={s.id} className="rsidebar-source-item">
                <span className="rsidebar-source-num">{s.id}</span>
                <div className="rsidebar-source-body">
                  <p className="rsidebar-source-title">{s.title}</p>
                  <p className="rsidebar-source-authors">{s.authors}</p>
                </div>
                <span className={`rsidebar-source-badge ${s.score >= 95 ? 'badge-high' : s.score >= 90 ? 'badge-med' : 'badge-low'}`}>
                  {s.score}%
                </span>
              </li>
            ))}
          </ol>
        </div>

        <div className="rsidebar-card">
          <div className="rsidebar-card-header">
            <span className="rsidebar-card-title">Quality Assessment</span>
            <span className="rsidebar-confidence-badge">High Confidence</span>
          </div>

          <div className="rsidebar-metrics">
            {qualityMetrics.map((m) => (
              <div key={m.label} className="rsidebar-metric-row">
                <span className="rsidebar-metric-label">{m.label}</span>
                <ScoreBar value={m.value} />
                <span className="rsidebar-metric-value">{m.value.toFixed(2)}</span>
              </div>
            ))}

            <div className="rsidebar-overall-row">
              <span className="rsidebar-metric-label">Overall Confidence</span>
              <ScoreBar value={parseFloat(overallConfidence)} />
              <span className="rsidebar-metric-value rsidebar-metric-bold">{overallConfidence}</span>
            </div>
          </div>

          <p className="rsidebar-quality-note">
            The review is well-supported by recent, high-quality sources with good coverage of the topic.
          </p>
        </div>

        <div className="rsidebar-card rsidebar-upload-card">
          <div className="rsidebar-card-header">
            <span className="rsidebar-card-title">Upload</span>
          </div>
          <div className="rsidebar-upload-zone">
            <i className="material-icons rsidebar-upload-icon">upload_file</i>
            <p className="rsidebar-upload-hint">Drop files here or <button className="rsidebar-upload-link">browse</button></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default R_Sidebar;
