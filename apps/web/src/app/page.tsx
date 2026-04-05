import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm flex flex-col group">
        <h1 className="text-6xl font-bold text-gray-900 mb-6 tracking-tight transition group-hover:scale-105">JobTailor</h1>
        <p className="text-xl text-gray-600 mb-12 text-center max-w-2xl">
          Upload your resume and LinkedIn profile. Let our engine tailor your documents to any job description instantly.
        </p>

        <a 
          href="http://localhost:8000/api/auth/login/linkedin"
          className="flex items-center px-8 py-4 bg-[#0077b5] text-white rounded-full font-semibold text-lg shadow-lg hover:bg-[#005582] transition-colors"
        >
          <svg className="w-6 h-6 mr-3" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
          Sign in with LinkedIn
        </a>
      </div>
    </main>
  );
}
