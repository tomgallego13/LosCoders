import React from 'react';
import { Upload } from 'lucide-react';

const UIWireframe = () => {
  return (
    <div className="w-full h-96 bg-gray-50 p-6 rounded-lg shadow-sm">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Quiz Format Converter</h1>
        <p className="text-gray-600">Convert AI-generated test banks to Canvas/Respondus format</p>
      </header>
      
      <div className="grid grid-cols-2 gap-6">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center">
          <Upload size={48} className="text-blue-500 mb-4" />
          <p className="text-gray-700 mb-2">Drop your test bank file here</p>
          <p className="text-sm text-gray-500">Supported formats: .txt, .docx, .pdf</p>
        </div>
        
        <div className="border border-gray-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-4">Output Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Output Format</label>
              <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                <option>Canvas Quiz</option>
                <option>Respondus</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Question Types</label>
              <div className="mt-2 space-y-2">
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300" defaultChecked />
                  <span className="ml-2 text-sm">Multiple Choice</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300" defaultChecked />
                  <span className="ml-2 text-sm">True/False</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
          Convert and Download
        </button>
      </div>
    </div>
  );
};

export default UIWireframe;