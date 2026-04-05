/**
 * Screenshot viewer — gallery of run screenshots.
 */

import { useState } from 'react';
import { Image, X, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Screenshot } from '../types';
import './ScreenshotViewer.css';

interface ScreenshotViewerProps {
  screenshots: Screenshot[];
  loading?: boolean;
}

export default function ScreenshotViewer({ screenshots, loading = false }: ScreenshotViewerProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  if (loading) {
    return (
      <div className="screenshot-viewer" id="screenshot-viewer">
        <div className="screenshot-viewer__header">
          <Image size={16} />
          <span>Screenshots</span>
        </div>
        <div className="screenshot-viewer__empty">Loading screenshots...</div>
      </div>
    );
  }

  return (
    <div className="screenshot-viewer" id="screenshot-viewer">
      <div className="screenshot-viewer__header">
        <Image size={16} />
        <span>Screenshots ({screenshots.length})</span>
      </div>

      {screenshots.length === 0 ? (
        <div className="screenshot-viewer__empty">
          <Image size={32} />
          <span>No screenshots for this run</span>
        </div>
      ) : (
        <div className="screenshot-viewer__grid">
          {screenshots.map((ss, index) => (
            <div
              key={ss.filename}
              className="screenshot-thumb"
              onClick={() => setSelectedIndex(index)}
            >
              <div className="screenshot-thumb__placeholder">
                <Image size={24} />
              </div>
              <span className="screenshot-thumb__name">{ss.filename}</span>
            </div>
          ))}
        </div>
      )}

      {/* Lightbox */}
      {selectedIndex !== null && (
        <div className="screenshot-lightbox" onClick={() => setSelectedIndex(null)}>
          <div className="screenshot-lightbox__content" onClick={e => e.stopPropagation()}>
            <button className="screenshot-lightbox__close" onClick={() => setSelectedIndex(null)}>
              <X size={20} />
            </button>
            <div className="screenshot-lightbox__image">
              <Image size={64} />
              <span>{screenshots[selectedIndex].filename}</span>
            </div>
            <div className="screenshot-lightbox__nav">
              <button
                disabled={selectedIndex === 0}
                onClick={() => setSelectedIndex(Math.max(0, selectedIndex - 1))}
              >
                <ChevronLeft size={20} />
              </button>
              <span>{selectedIndex + 1} / {screenshots.length}</span>
              <button
                disabled={selectedIndex === screenshots.length - 1}
                onClick={() => setSelectedIndex(Math.min(screenshots.length - 1, selectedIndex + 1))}
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
