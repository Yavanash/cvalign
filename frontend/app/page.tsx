"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Upload,
  FileText,
  Trash2,
  RotateCcw,
  Trophy,
  User,
  Star,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  TrendingUp,
} from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface LeaderboardEntry {
  username: string
  score: number
  timestamp?: string
}

interface ScoreResponse {
  relevance_score: number
  assessment: string
  strengths: string[]
  drawbacks: string[]
  recommendations: string[]
}

export default function ResumeScreener() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState("")
  const [candidateName, setCandidateName] = useState("")
  const [scoreResponse, setScoreResponse] = useState<ScoreResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  // Fetch leaderboard data on component mount
  useEffect(() => {
    fetchLeaderboardFromServer()
  }, [])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setErrorMessage("")
      setScoreResponse(null)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setErrorMessage("Please select a PDF file first.")
      return
    }

    if (!jobDescription.trim()) {
      setErrorMessage("Job description cannot be blank")
      return
    }

    setIsAnalyzing(true)
    setErrorMessage("")
    setScoreResponse(null)

    const formData = new FormData()
    formData.append("pdf", selectedFile)
    formData.append("job_desc", jobDescription)
    formData.append("candidate_name", candidateName)

    try {
      const res = await fetch("http://localhost:8080/score", {
        method: "POST",
        body: formData,
      })

      if (!res.ok) {
        const errText = await res.text()
        setErrorMessage(`Server error: ${res.status}\n${errText}`)
        return
      }

      const data: ScoreResponse = await res.json()
      setScoreResponse(data)

      // Refresh leaderboard after successful analysis
      await fetchLeaderboardFromServer()
    } catch (err) {
      console.error("Analysis error:", err)
      setErrorMessage("Analysis failed: " + (err as Error).message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleClear = () => {
    setScoreResponse(null)
    setErrorMessage("")
  }

  const handleUnselectFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
    setScoreResponse(null)
    setErrorMessage("")
  }

  const fetchLeaderboardFromServer = async () => {
    try {
      const res = await fetch("http://localhost:8080/v1/leaderboard")
      if (!res.ok) {
        console.error("Failed to fetch leaderboard:", res.statusText)
        return
      }

      const json = await res.json()
      setLeaderboardData(json.data || [])
    } catch (err) {
      console.error("Error fetching leaderboard:", err)
    }
  }

  const handleRefreshLeaderboard = async () => {
    setIsRefreshing(true)
    await fetchLeaderboardFromServer()
    setTimeout(() => setIsRefreshing(false), 500)
  }

  const handleClearLeaderboard = async () => {
    try {
      const res = await fetch("http://localhost:8080/v1/leaderboard", {
        method: "DELETE",
      })
      if (res.ok) {
        setLeaderboardData([])
      }
    } catch (err) {
      console.error("Error clearing leaderboard:", err)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return "default"
    if (score >= 60) return "secondary"
    return "destructive"
  }

  const getRankBadgeVariant = (rank: number) => {
    switch (rank) {
      case 1:
        return "default"
      case 2:
        return "secondary"
      case 3:
        return "outline"
      default:
        return "outline"
    }
  }

  const getRankIcon = (rank: number) => {
    if (rank <= 3) {
      return <Trophy className="h-4 w-4" />
    }
    return <Star className="h-4 w-4" />
  }

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return ""
    try {
      return new Date(timestamp).toLocaleString()
    } catch {
      return timestamp
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">CVAlign</h1>
          <p className="text-lg text-gray-600">Advanced resume evaluation with detailed insights and recommendations</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload Resume
                </CardTitle>
                <CardDescription>
                  Upload a PDF resume and provide job details for comprehensive AI evaluation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label htmlFor="pdfFile" className="block text-sm font-medium mb-2">
                    Select PDF Resume *
                  </label>
                  <Input
                    id="pdfFile"
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="cursor-pointer"
                  />
                  {selectedFile && (
                    <div className="mt-2 flex items-center gap-2 text-sm text-green-600">
                      <FileText className="h-4 w-4" />
                      {selectedFile.name} ({Math.round(selectedFile.size / 1024)} KB)
                    </div>
                  )}
                </div>

                <div>
                  <label htmlFor="candidate" className="block text-sm font-medium mb-2">
                    Candidate Name
                  </label>
                  <Input
                    id="candidate"
                    placeholder="Enter candidate name (optional)"
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                  />
                </div>

                <div>
                  <label htmlFor="job_desc" className="block text-sm font-medium mb-2">
                    Job Description *
                  </label>
                  <Textarea
                    id="job_desc"
                    placeholder="Paste the complete job description here..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    rows={6}
                    className="resize-none"
                  />
                </div>

                <div className="flex gap-2 flex-wrap">
                  <Button onClick={handleAnalyze} disabled={isAnalyzing} className="flex-1 sm:flex-none">
                    {isAnalyzing ? "Analyzing..." : "Analyze Resume"}
                  </Button>
                  <Button variant="outline" onClick={handleClear}>
                    Clear Results
                  </Button>
                  <Button variant="outline" onClick={handleUnselectFile}>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Unselect File
                  </Button>
                </div>

                {errorMessage && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-800">{errorMessage}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Results Section */}
            {scoreResponse && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Analysis Results</span>
                    <Badge variant={getScoreBadgeVariant(scoreResponse.relevance_score)} className="text-lg px-3 py-1">
                      {scoreResponse.relevance_score.toFixed(1)}%
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Overall Assessment */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      Overall Assessment
                    </h3>
                    <p className="text-gray-700 leading-relaxed">{scoreResponse.assessment}</p>
                  </div>

                  <Separator />

                  {/* Strengths */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-green-700">
                      <CheckCircle className="h-5 w-5" />
                      Strengths
                    </h3>
                    <div className="space-y-2">
                      {scoreResponse.strengths.map((strength, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                          <p className="text-gray-700">{strength}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Separator />

                  {/* Areas for Improvement */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-orange-700">
                      <AlertCircle className="h-5 w-5" />
                      Areas for Improvement
                    </h3>
                    <div className="space-y-2">
                      {scoreResponse.drawbacks.map((drawback, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                          <p className="text-gray-700">{drawback}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Separator />

                  {/* Recommendations */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-blue-700">
                      <Lightbulb className="h-5 w-5" />
                      Recommendations
                    </h3>
                    <div className="space-y-2">
                      {scoreResponse.recommendations.map((recommendation, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                          <p className="text-gray-700">{recommendation}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Leaderboard Section */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Trophy className="h-5 w-5" />
                    Leaderboard
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleRefreshLeaderboard}
                      disabled={isRefreshing}
                      className={isRefreshing ? "animate-spin" : ""}
                    >
                      <RotateCcw className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleClearLeaderboard}>
                      Clear
                    </Button>
                  </div>
                </CardTitle>
                <CardDescription>Top candidates ranked by relevance score</CardDescription>
              </CardHeader>
              <CardContent>
                {leaderboardData.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Trophy className="h-12 w-12 mx-auto mb-2 opacity-30" />
                    <p>No submissions yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {leaderboardData.map((entry, index) => {
                      const rank = index + 1
                      return (
                        <div
                          key={`${entry.username}-${index}`}
                          className={`flex items-center gap-3 p-3 rounded-lg border ${
                            rank <= 3
                              ? "bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200"
                              : "bg-gray-50 border-gray-200"
                          }`}
                        >
                          <Badge variant={getRankBadgeVariant(rank)} className="flex items-center gap-1">
                            {getRankIcon(rank)}#{rank}
                          </Badge>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <User className="h-4 w-4 text-gray-500" />
                              <p className="font-medium truncate">{entry.username}</p>
                            </div>
                            {entry.timestamp && (
                              <p className="text-xs text-gray-500 mt-1">{formatTimestamp(entry.timestamp)}</p>
                            )}
                          </div>
                          <div className="text-right">
                            <p className={`font-bold text-lg ${getScoreColor(entry.score)}`}>
                              {entry.score.toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
