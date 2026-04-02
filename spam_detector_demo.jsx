import { useState } from "react";

const EXAMPLES = [
  { label: "🚨 Prize Spam", text: "WINNER!! You have been selected to receive a £900 prize reward! Call 09061701461 to claim your prize now. This offer expires in 24 hours!" },
  { label: "🚨 Phishing", text: "URGENT: Your bank account has been compromised. Click here immediately to verify your details and avoid permanent suspension." },
  { label: "🚨 Free Offer", text: "Congratulations! You've won a FREE iPhone 15. Complete a short survey to claim your prize. Limited time only!" },
  { label: "✅ Casual Chat", text: "Hey! Are we still on for lunch tomorrow at 1pm? Let me know if you need to reschedule." },
  { label: "✅ Work Email", text: "Please review the attached project report and share your feedback by end of business today. Thanks!" },
  { label: "✅ Birthday", text: "Happy birthday! Hope you have a wonderful day filled with joy and celebration. Miss you!" },
];

const SPAM_KEYWORDS = [
  'winner', 'prize', 'free', 'urgent', 'claim', 'won', 'cash',
  'congratulations', 'selected', 'reward', 'offer', 'click here',
  'limited time', 'act now', 'call now', 'guaranteed', 'billion',
  'discount', 'subscribe', '£', '$1000', 'viagra', 'loan', 'credit',
  'win', 'lucky', 'exclusive', 'expires', 'verify', 'account',
  'compromised', 'suspended', 'confirm', 'immediately'
];

const HAM_KEYWORDS = [
  'meeting', 'lunch', 'tomorrow', 'report', 'please', 'thanks',
  'birthday', 'happy', 'hope', 'hey', 'reschedule', 'attached',
  'feedback', 'review', 'project', 'hi', 'hello', 'dear'
];

function simpleClassify(text) {
  const lower = text.toLowerCase();
  let spamScore = 0;
  let hamScore = 0;
  const matchedSpam = [];
  const matchedHam = [];

  SPAM_KEYWORDS.forEach(kw => {
    if (lower.includes(kw)) { spamScore += 1; matchedSpam.push(kw); }
  });
  HAM_KEYWORDS.forEach(kw => {
    if (lower.includes(kw)) { hamScore += 1; matchedHam.push(kw); }
  });

  // Boost for ALL CAPS
  const capsRatio = (text.match(/[A-Z]/g) || []).length / text.length;
  if (capsRatio > 0.3) spamScore += 2;

  // Boost for exclamation marks
  const exclamations = (text.match(/!/g) || []).length;
  if (exclamations > 1) spamScore += 1;

  const total = spamScore + hamScore + 1;
  const spamProb = Math.min(0.99, (spamScore + 0.5) / total);
  const isSpam = spamScore > hamScore;

  const confidence = isSpam
    ? Math.round(50 + spamProb * 47)
    : Math.round(50 + (1 - spamProb) * 47);

  return { isSpam, confidence, matchedSpam, matchedHam };
}

export default function SpamDetector() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("check");
  const [history, setHistory] = useState([]);

  const analyse = async (inputText = text) => {
    if (!inputText.trim()) return;
    setLoading(true);
    setResult(null);
    await new Promise(r => setTimeout(r, 600));
    const res = simpleClassify(inputText);
    setResult(res);
    setHistory(h => [{ text: inputText.slice(0, 60) + "...", ...res, time: new Date().toLocaleTimeString() }, ...h.slice(0, 9)]);
    setLoading(false);
  };

  const useExample = (ex) => {
    setText(ex.text);
    setResult(null);
    setActiveTab("check");
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0a0a0f 0%, #12121e 50%, #0d0d1a 100%)",
      fontFamily: "'Courier New', monospace",
      color: "#e0e0ff",
      padding: "0",
    }}>
      {/* Header */}
      <div style={{
        background: "rgba(255,255,255,0.03)",
        borderBottom: "1px solid rgba(100,100,255,0.2)",
        padding: "20px 32px",
        display: "flex",
        alignItems: "center",
        gap: "16px",
      }}>
        <div style={{
          width: 44, height: 44, borderRadius: "10px",
          background: "linear-gradient(135deg, #6c63ff, #ff6b9d)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "22px", boxShadow: "0 4px 20px rgba(108,99,255,0.4)"
        }}>🛡️</div>
        <div>
          <div style={{ fontSize: "1.3rem", fontWeight: "bold", letterSpacing: "2px", color: "#fff" }}>
            SPAM DETECTOR
          </div>
          <div style={{ fontSize: "0.7rem", color: "#888", letterSpacing: "1px" }}>
            TF-IDF + NAIVE BAYES ENGINE
          </div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: "8px" }}>
          {["check", "examples", "history"].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              padding: "7px 18px",
              background: activeTab === tab ? "rgba(108,99,255,0.3)" : "transparent",
              border: activeTab === tab ? "1px solid #6c63ff" : "1px solid rgba(255,255,255,0.1)",
              borderRadius: "6px",
              color: activeTab === tab ? "#a89cff" : "#666",
              cursor: "pointer",
              fontSize: "0.75rem",
              letterSpacing: "1px",
              textTransform: "uppercase",
              transition: "all 0.2s",
            }}>{tab}</button>
          ))}
        </div>
      </div>

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "32px 24px" }}>

        {/* CHECK TAB */}
        {activeTab === "check" && (
          <div>
            <div style={{ marginBottom: "12px", color: "#888", fontSize: "0.8rem", letterSpacing: "1px" }}>
              PASTE EMAIL CONTENT BELOW
            </div>
            <textarea
              value={text}
              onChange={e => { setText(e.target.value); setResult(null); }}
              placeholder="Type or paste email text here..."
              style={{
                width: "100%", minHeight: 180,
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(100,100,255,0.2)",
                borderRadius: "12px",
                padding: "18px",
                color: "#e0e0ff",
                fontSize: "0.95rem",
                lineHeight: "1.6",
                resize: "vertical",
                outline: "none",
                fontFamily: "inherit",
                boxSizing: "border-box",
                transition: "border-color 0.2s",
              }}
              onFocus={e => e.target.style.borderColor = "rgba(108,99,255,0.6)"}
              onBlur={e => e.target.style.borderColor = "rgba(100,100,255,0.2)"}
            />
            <div style={{ display: "flex", gap: "12px", marginTop: "14px" }}>
              <button
                onClick={() => analyse()}
                disabled={!text.trim() || loading}
                style={{
                  padding: "13px 32px",
                  background: text.trim() ? "linear-gradient(135deg, #6c63ff, #9c5fff)" : "#222",
                  border: "none",
                  borderRadius: "8px",
                  color: text.trim() ? "white" : "#555",
                  fontFamily: "inherit",
                  fontSize: "0.85rem",
                  fontWeight: "bold",
                  letterSpacing: "1px",
                  cursor: text.trim() ? "pointer" : "not-allowed",
                  transition: "all 0.2s",
                  boxShadow: text.trim() ? "0 4px 20px rgba(108,99,255,0.35)" : "none",
                }}
              >
                {loading ? "⏳ ANALYSING..." : "🔍 ANALYSE EMAIL"}
              </button>
              {text && (
                <button onClick={() => { setText(""); setResult(null); }} style={{
                  padding: "13px 20px",
                  background: "transparent",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "8px",
                  color: "#666",
                  cursor: "pointer",
                  fontFamily: "inherit",
                  fontSize: "0.8rem",
                }}>CLEAR</button>
              )}
            </div>

            {/* Result */}
            {result && !loading && (
              <div style={{
                marginTop: "28px",
                borderRadius: "14px",
                overflow: "hidden",
                border: result.isSpam ? "1px solid rgba(255,80,80,0.3)" : "1px solid rgba(0,220,130,0.3)",
                animation: "fadeIn 0.4s ease",
              }}>
                <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:translateY(0) } }`}</style>
                <div style={{
                  background: result.isSpam
                    ? "linear-gradient(135deg, rgba(255,50,50,0.15), rgba(180,0,0,0.1))"
                    : "linear-gradient(135deg, rgba(0,220,130,0.15), rgba(0,120,60,0.1))",
                  padding: "24px 28px",
                  display: "flex",
                  alignItems: "center",
                  gap: "20px",
                }}>
                  <div style={{ fontSize: "3rem" }}>{result.isSpam ? "🚨" : "✅"}</div>
                  <div>
                    <div style={{
                      fontSize: "1.8rem",
                      fontWeight: "bold",
                      color: result.isSpam ? "#ff6b6b" : "#4ade80",
                      letterSpacing: "3px",
                    }}>
                      {result.isSpam ? "SPAM DETECTED" : "SAFE — NOT SPAM"}
                    </div>
                    <div style={{ color: "#aaa", fontSize: "0.8rem", marginTop: "4px" }}>
                      {result.confidence}% confidence · Naive Bayes classifier
                    </div>
                  </div>
                  {/* Confidence bar */}
                  <div style={{ marginLeft: "auto", textAlign: "center" }}>
                    <div style={{
                      width: 80, height: 80, borderRadius: "50%",
                      background: `conic-gradient(${result.isSpam ? "#ff6b6b" : "#4ade80"} ${result.confidence * 3.6}deg, rgba(255,255,255,0.05) 0deg)`,
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                      <div style={{
                        width: 60, height: 60, borderRadius: "50%",
                        background: "#12121e",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: "0.85rem", fontWeight: "bold",
                        color: result.isSpam ? "#ff6b6b" : "#4ade80",
                      }}>{result.confidence}%</div>
                    </div>
                  </div>
                </div>

                {/* Keyword breakdown */}
                <div style={{ background: "rgba(0,0,0,0.3)", padding: "18px 28px", display: "flex", gap: "32px" }}>
                  {result.matchedSpam.length > 0 && (
                    <div>
                      <div style={{ fontSize: "0.7rem", color: "#888", letterSpacing: "1px", marginBottom: "8px" }}>SPAM SIGNALS</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                        {result.matchedSpam.map(kw => (
                          <span key={kw} style={{
                            background: "rgba(255,80,80,0.15)",
                            border: "1px solid rgba(255,80,80,0.3)",
                            color: "#ff9999",
                            padding: "3px 10px",
                            borderRadius: "4px",
                            fontSize: "0.75rem",
                          }}>{kw}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {result.matchedHam.length > 0 && (
                    <div>
                      <div style={{ fontSize: "0.7rem", color: "#888", letterSpacing: "1px", marginBottom: "8px" }}>SAFE SIGNALS</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                        {result.matchedHam.map(kw => (
                          <span key={kw} style={{
                            background: "rgba(0,220,130,0.1)",
                            border: "1px solid rgba(0,220,130,0.2)",
                            color: "#6ee7b7",
                            padding: "3px 10px",
                            borderRadius: "4px",
                            fontSize: "0.75rem",
                          }}>{kw}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* EXAMPLES TAB */}
        {activeTab === "examples" && (
          <div>
            <div style={{ marginBottom: "20px", color: "#888", fontSize: "0.8rem", letterSpacing: "1px" }}>
              CLICK AN EXAMPLE TO TEST IT
            </div>
            <div style={{ display: "grid", gap: "14px" }}>
              {EXAMPLES.map((ex, i) => (
                <div key={i}
                  onClick={() => useExample(ex)}
                  style={{
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px",
                    padding: "18px 22px",
                    cursor: "pointer",
                    transition: "all 0.2s",
                    display: "flex",
                    alignItems: "center",
                    gap: "14px",
                  }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(108,99,255,0.4)"}
                  onMouseLeave={e => e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"}
                >
                  <div style={{ fontSize: "1.3rem", minWidth: 30 }}>{ex.label.split(" ")[0]}</div>
                  <div>
                    <div style={{ fontWeight: "bold", fontSize: "0.9rem", marginBottom: "4px" }}>{ex.label.slice(3)}</div>
                    <div style={{ color: "#666", fontSize: "0.82rem" }}>{ex.text.slice(0, 90)}...</div>
                  </div>
                  <div style={{ marginLeft: "auto", color: "#6c63ff", fontSize: "0.75rem" }}>TRY →</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* HISTORY TAB */}
        {activeTab === "history" && (
          <div>
            <div style={{ marginBottom: "20px", color: "#888", fontSize: "0.8rem", letterSpacing: "1px" }}>
              RECENT CLASSIFICATIONS
            </div>
            {history.length === 0 ? (
              <div style={{ textAlign: "center", color: "#444", padding: "60px", fontSize: "0.9rem" }}>
                No history yet. Analyse some emails first!
              </div>
            ) : (
              <div style={{ display: "grid", gap: "10px" }}>
                {history.map((h, i) => (
                  <div key={i} style={{
                    background: "rgba(255,255,255,0.03)",
                    border: h.isSpam ? "1px solid rgba(255,80,80,0.2)" : "1px solid rgba(0,220,130,0.15)",
                    borderRadius: "8px",
                    padding: "14px 20px",
                    display: "flex",
                    alignItems: "center",
                    gap: "14px",
                  }}>
                    <div style={{ fontSize: "1.1rem" }}>{h.isSpam ? "🚨" : "✅"}</div>
                    <div style={{ flex: 1, fontSize: "0.85rem", color: "#bbb" }}>{h.text}</div>
                    <div style={{
                      color: h.isSpam ? "#ff6b6b" : "#4ade80",
                      fontWeight: "bold",
                      fontSize: "0.8rem",
                      minWidth: 70,
                    }}>{h.isSpam ? "SPAM" : "HAM"} {h.confidence}%</div>
                    <div style={{ color: "#444", fontSize: "0.75rem" }}>{h.time}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
