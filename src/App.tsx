/// <reference types="vite/client" />
import { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileAudio, CheckCircle, Loader2, Download, AlertCircle } from 'lucide-react';

type AppState = 'idle' | 'processing' | 'success' | 'error';

function App() {
  const [state, setState] = useState<AppState>('idle');
  const [downloadUrl, setDownloadUrl] = useState<string>('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      // Vercel Serverless Function Limit is 4.5MB
      if (selectedFile.size > 4.5 * 1024 * 1024) {
        setErrorMsg("File is too large for Vercel Demo (Max 4.5MB). Please use a shorter audio clip.");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setErrorMsg('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !linkedinUrl) {
      setErrorMsg("Please provide both a LinkedIn URL and an audio file.");
      return;
    }

    setState('processing');
    setErrorMsg('');

    const formData = new FormData();
    formData.append('linkedin_url', linkedinUrl);
    formData.append('file', file);

    try {
      // Use relative path for Vercel (rewrites will handle it)
      // Locally, you might need a proxy in vite.config.ts or just rely on CORS if running separately.
      // For Vercel deployment:
      const apiUrl = import.meta.env.PROD ? '/api/generate-proposal' : 'http://127.0.0.1:8000/api/generate-proposal';

      const response = await axios.post(apiUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.status === 'success') {
        setDownloadUrl(response.data.pdf_url);
        setState('success');
      } else {
        throw new Error('Generation failed');
      }
    } catch (err: any) {
      console.error(err);
      setState('error');
      setErrorMsg(err.response?.data?.detail || "Something went wrong. Please try again.");
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-4 relative">

      {/* Background Orbs */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-primary/20 rounded-full blur-[100px] pointer-events-none -translate-x-1/2 -translate-y-1/2" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-[100px] pointer-events-none translate-x-1/2 translate-y-1/2" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-xl w-full"
      >
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Proposal<span className="text-primary">Gen</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Turn sales calls into closed deals with AI-driven proposals.
          </p>
        </div>

        <div className="glass-card rounded-2xl p-8 relative overflow-hidden">
          <AnimatePresence mode="wait">
            {state === 'idle' && (
              <motion.form
                key="form"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, x: -20 }}
                onSubmit={handleSubmit}
                className="space-y-6"
              >
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">LinkedIn Profile URL</label>
                  <input
                    type="url"
                    placeholder="https://linkedin.com/in/prospect"
                    value={linkedinUrl}
                    onChange={(e) => setLinkedinUrl(e.target.value)}
                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Upload Call Recording</label>
                  <div className="relative group">
                    <input
                      type="file"
                      accept="audio/*"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    />
                    <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${file ? 'border-primary/50 bg-primary/5' : 'border-white/10 hover:border-white/20 bg-black/20'}`}>
                      {file ? (
                        <div className="flex flex-col items-center text-primary">
                          <FileAudio size={32} className="mb-2" />
                          <span className="font-medium text-white">{file.name}</span>
                          <span className="text-xs text-gray-400 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                        </div>
                      ) : (
                        <div className="flex flex-col items-center text-gray-400 group-hover:text-gray-300">
                          <Upload size={32} className="mb-2" />
                          <span className="font-medium">Click to upload or drag and drop</span>
                          <span className="text-xs mt-1">MP3, M4A, WAV supported</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {errorMsg && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-200 text-sm">
                    <AlertCircle size={16} />
                    {errorMsg}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!file || !linkedinUrl}
                  className="w-full bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white font-semibold py-4 rounded-xl shadow-lg shadow-primary/25 transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Generate Proposal
                </button>
              </motion.form>
            )}

            {state === 'processing' && (
              <motion.div
                key="processing"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex flex-col items-center justify-center py-12 text-center"
              >
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-primary/30 blur-xl rounded-full animate-pulse" />
                  <Loader2 size={64} className="text-primary animate-spin relative z-10" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">Analyzing Conversation</h3>
                <p className="text-gray-400 max-w-xs mx-auto">
                  Listening to audio, scraping LinkedIn, and crafting the perfect strategy...
                </p>
              </motion.div>
            )}

            {state === 'success' && (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center py-8 text-center"
              >
                <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mb-6 text-green-400 border border-green-500/30">
                  <CheckCircle size={40} />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">Proposal Ready!</h3>
                <p className="text-gray-400 mb-8">
                  Your bespoke proposal has been generated and is ready for download.
                </p>

                <a
                  href={downloadUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 bg-white text-black font-bold px-8 py-4 rounded-xl hover:bg-gray-100 transition-colors shadow-lg shadow-white/10"
                >
                  <Download size={20} />
                  Download PDF
                </a>

                <button
                  onClick={() => {
                    setState('idle');
                    setFile(null);
                    setLinkedinUrl('');
                    setDownloadUrl('');
                  }}
                  className="mt-6 text-sm text-gray-500 hover:text-white transition-colors"
                >
                  Generate Another
                </button>
              </motion.div>
            )}

            {state === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center py-8 text-center"
              >
                <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mb-6 text-red-400 border border-red-500/30">
                  <AlertCircle size={40} />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">Generation Failed</h3>
                <p className="text-gray-400 mb-8 max-w-xs mx-auto">
                  {errorMsg || "An unexpected error occurred."}
                </p>

                <button
                  onClick={() => setState('idle')}
                  className="bg-white/10 text-white font-medium px-6 py-3 rounded-xl hover:bg-white/20 transition-colors"
                >
                  Try Again
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="text-center mt-8 text-xs text-gray-600">
          Powered by Autonomous Sales Engineering Agent
        </div>
      </motion.div>
    </div>
  )
}

export default App
