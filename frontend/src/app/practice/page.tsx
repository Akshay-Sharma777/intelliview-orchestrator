"use client";

import { useState } from "react";
import { staticQuestionBank } from "@/lib/questionBank";

export default function PracticePage() {
  const companies = Object.keys(staticQuestionBank);

  const [selectedCompany, setSelectedCompany] = useState<string>(
    companies[0] || ""
  );

  const currentQuestions = staticQuestionBank[selectedCompany] || [];

  return (
    <main className="mx-auto max-w-4xl p-6 md:p-8">
      <header className="mb-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">
          Company Practice
        </h1>

        <p className="text-gray-600">
          Select a company to view practice questions from the static question
          bank.
        </p>
      </header>

      {/* Company Selector */}
      <section className="mb-8">
        <label
          htmlFor="company-select"
          className="mb-2 block text-sm font-medium text-gray-700"
        >
          Select Target Company
        </label>

        <select
          id="company-select"
          value={selectedCompany}
          onChange={(event) => setSelectedCompany(event.target.value)}
          className="w-full rounded-md border border-gray-300 bg-white p-2.5 text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 md:w-1/2"
        >
          {companies.map((company) => (
            <option key={company} value={company}>
              {company}
            </option>
          ))}
        </select>
      </section>

      {/* Questions List */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-800">
          {selectedCompany
            ? `${selectedCompany} Questions`
            : "Practice Questions"}
        </h2>

        {currentQuestions.length > 0 ? (
          <ul className="space-y-3">
            {currentQuestions.map((question, index) => (
              <li
                key={`${selectedCompany}-${index}`}
                className="rounded-lg border border-gray-200 bg-white p-4 text-gray-800 shadow-sm"
              >
                <span className="mr-2 font-semibold text-gray-500">
                  {index + 1}.
                </span>
                {question}
              </li>
            ))}
          </ul>
        ) : (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-gray-500">
            No questions available for this company.
          </div>
        )}
      </section>
    </main>
  );
}