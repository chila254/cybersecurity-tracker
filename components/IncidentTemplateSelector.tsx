'use client'

import { incidentTemplates } from '@/lib/incident-templates'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'
import { useState } from 'react'

interface IncidentTemplateSelectorProps {
  onSelect: (template: typeof incidentTemplates[0]) => void
  onClose: () => void
}

export function IncidentTemplateSelector({ onSelect, onClose }: IncidentTemplateSelectorProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const selectedTemplate = incidentTemplates.find(t => t.id === selectedId)

  const handleSelect = () => {
    if (selectedTemplate) {
      onSelect(selectedTemplate)
      onClose()
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-700">
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <AlertCircle className="h-6 w-6 text-blue-400" />
            Select Incident Template
          </h2>
          <p className="text-slate-400 text-sm mt-1">Choose a template to pre-fill incident details</p>
        </div>

        <div className="p-6 space-y-3">
          {incidentTemplates.map(template => (
            <button
              key={template.id}
              onClick={() => setSelectedId(template.id)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                selectedId === template.id
                  ? 'border-blue-500 bg-blue-900/20'
                  : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-white">{template.name}</h3>
                  <p className="text-slate-400 text-sm mt-1">{template.description}</p>
                  <div className="flex gap-2 mt-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      template.severity === 'CRITICAL' ? 'bg-red-900/30 text-red-300' :
                      template.severity === 'HIGH' ? 'bg-orange-900/30 text-orange-300' :
                      template.severity === 'MEDIUM' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-blue-900/30 text-blue-300'
                    }`}>
                      {template.severity}
                    </span>
                    <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">
                      {template.checklist_items.length} checklist items
                    </span>
                  </div>
                </div>
                <input
                  type="radio"
                  checked={selectedId === template.id}
                  onChange={() => setSelectedId(template.id)}
                  className="mt-2"
                />
              </div>
            </button>
          ))}
        </div>

        {selectedTemplate && (
          <div className="border-t border-slate-700 bg-slate-800/50 p-6">
            <h4 className="font-semibold text-white mb-3">Checklist items</h4>
            <ul className="space-y-2">
              {selectedTemplate.checklist_items.slice(0, 5).map((item, i) => (
                <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                  <span className="text-blue-400 mt-1">✓</span>
                  {item}
                </li>
              ))}
              {selectedTemplate.checklist_items.length > 5 && (
                <li className="text-slate-400 text-sm italic">
                  +{selectedTemplate.checklist_items.length - 5} more items
                </li>
              )}
            </ul>
          </div>
        )}

        <div className="border-t border-slate-700 p-6 flex gap-3 justify-end">
          <Button
            onClick={onClose}
            variant="outline"
            className="bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSelect}
            disabled={!selectedTemplate}
            className="bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
          >
            Use Template
          </Button>
        </div>
      </div>
    </div>
  )
}
