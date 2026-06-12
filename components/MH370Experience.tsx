"use client";

import {
  BookOpen,
  ChevronRight,
  Clock3,
  Compass,
  ExternalLink,
  Info,
  Plane,
  Radio,
  Radar,
  Search,
  ShieldAlert,
  Ship,
  Satellite,
  Waves,
} from "lucide-react";
import {
  type ComponentType,
  type CSSProperties,
  type KeyboardEvent,
  type PointerEvent,
  type ReactNode,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

type TabId = "controversies" | "overview" | "timeline" | "evidence" | "search" | "apush" | "legacy" | "sources";
type TimelineFilter = "all" | "flight" | "search" | "debris" | "policy" | "today";
type SourceId =
  | "mot"
  | "mot2026"
  | "atsb"
  | "navy"
  | "icao"
  | "ap"
  | "ocean"
  | "aviationtoday"
  | "theweek"
  | "guardian";

type Source = {
  id: SourceId;
  name: string;
  label: string;
  href: string;
};

type ControversyCase = {
  id: string;
  title: string;
  short: string;
  status: "Serious theory" | "Speculative" | "Fringe";
  score: number;
  claim: string;
  whyItSpread: string;
  evidenceCheck: string;
  verdict: string;
  apush: string;
  sources: SourceId[];
};

type TimelineEvent = {
  id: string;
  date: string;
  time?: string;
  title: string;
  filter: Exclude<TimelineFilter, "all">;
  kicker: string;
  what: string;
  matters: string;
  apush: string;
  source: SourceId;
};

type Tab = {
  id: TabId;
  label: string;
  icon: ComponentType<{ className?: string }>;
};

const tabs: Tab[] = [
  { id: "controversies", label: "Theories & Evidence", icon: ShieldAlert },
  { id: "overview", label: "Case File", icon: Plane },
  { id: "timeline", label: "Timeline", icon: Clock3 },
  { id: "evidence", label: "Evidence", icon: Radar },
  { id: "search", label: "Search", icon: Search },
  { id: "apush", label: "APUSH", icon: BookOpen },
  { id: "legacy", label: "Legacy", icon: ShieldAlert },
  { id: "sources", label: "Sources", icon: ExternalLink },
];

const filters: { id: TimelineFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "flight", label: "Flight" },
  { id: "search", label: "Search" },
  { id: "debris", label: "Debris" },
  { id: "policy", label: "Policy" },
  { id: "today", label: "Today" },
];

const sources: Record<SourceId, Source> = {
  mot: {
    id: "mot",
    name: "Malaysia Ministry of Transport",
    label: "Official MH370 investigation archive",
    href: "https://www.mot.gov.my/en/aviation/reports/archived-report/mh370",
  },
  mot2026: {
    id: "mot2026",
    name: "Malaysia MOT / AAIB",
    label: "March 8, 2026 update to families",
    href: "https://www.mot.gov.my/en/Kenyataan%20Media/Year%202026/MH370%20Search%20Operation%202025-2026%20-%20Update%20to%20Families.pdf",
  },
  atsb: {
    id: "atsb",
    name: "Australian Transport Safety Bureau",
    label: "MH370 search overview",
    href: "https://www.atsb.gov.au/mh370-search-overview",
  },
  navy: {
    id: "navy",
    name: "U.S. Pacific Fleet",
    label: "P-8 Poseidon support in the MH370 search",
    href: "https://www.cpf.navy.mil/Newsroom/News/Article/2750384/us-7th-fleet-adds-second-p-8-poseidon-to-mh370-search/",
  },
  icao: {
    id: "icao",
    name: "International Civil Aviation Organization",
    label: "Aircraft tracking and GADSS",
    href: "https://www.icao.int/aircraft-tracking",
  },
  ap: {
    id: "ap",
    name: "Associated Press",
    label: "2026 renewed search update",
    href: "https://apnews.com/article/malaysia-missing-flight-mh370-seabed-search-5c564494723ae2d4ead87d7aeebcdef9",
  },
  ocean: {
    id: "ocean",
    name: "Ocean Infinity",
    label: "2026 search conclusion statement",
    href: "https://oceaninfinity.com/news/conclusion-of-the-search-for-malaysian-airlines-flight-mh370/",
  },
  aviationtoday: {
    id: "aviationtoday",
    name: "Aviation Today",
    label: "Final report and remote-control patent context",
    href: "https://www.aviationtoday.com/2018/08/02/malaysia-airlines-flight-370-final-report-inconclusive/",
  },
  theweek: {
    id: "theweek",
    name: "The Week",
    label: "Overview of theories and confirmed debris",
    href: "https://theweek.com/world-news/malaysia-airlines-flight-mh370-mystery",
  },
  guardian: {
    id: "guardian",
    name: "The Guardian",
    label: "Early conflicting media claims",
    href: "https://www.theguardian.com/world/2014/mar/13/malaysia-airlines-flight-mh370-media-claims",
  },
};

const controversyCases: ControversyCase[] = [
  {
    id: "pilot-directed",
    title: "Deliberate human action",
    short: "A serious but unproven explanation: someone intentionally redirected the aircraft.",
    status: "Serious theory",
    score: 3,
    claim:
      "A person with cockpit access or aircraft knowledge deliberately diverted MH370, possibly turning off communications and flying into the southern Indian Ocean.",
    whyItSpread:
      "The plane made unusual course changes after losing normal ATC contact, and the final report did not prove a mechanical failure.",
    evidenceCheck:
      "Investigators found clues that fit with a manual diversion, but the main wreckage and recorders are still missing. No one has proved a motive, exact sequence, or responsible person.",
    verdict:
      "Possible and widely discussed, but still not proven. It is fair to say a deliberate event is possible. It is not fair to say 'the pilot did it' as a fact.",
    apush:
      "This shows a very modern problem: people want a clear answer fast, but investigations sometimes move slowly because the evidence is incomplete.",
    sources: ["mot", "aviationtoday"],
  },
  {
    id: "diego-garcia",
    title: "Diego Garcia landing",
    short: "The plane was supposedly flown to a U.S. base in the Indian Ocean.",
    status: "Fringe",
    score: 1,
    claim:
      "MH370 was hijacked or secretly redirected to Diego Garcia, a U.S. military base, where it was hidden, shot down, or covered up.",
    whyItSpread:
      "The U.S. base was secretive and well known enough to make a cover-up story feel believable when the news was confusing.",
    evidenceCheck:
      "The satellite handshake analysis and search modeling pointed to the southern Indian Ocean, and debris later found along Indian Ocean shores supports an ocean crash rather than a base landing.",
    verdict:
      "Contradicted by the strongest public evidence. It mostly survives because secrecy makes cover-up stories feel dramatic and satisfying.",
    apush:
      "The theory reflects distrust of U.S. military power after the War on Terror and the long history of secrecy around overseas bases.",
    sources: ["atsb", "theweek"],
  },
  {
    id: "russian-plot",
    title: "Russian / Kazakhstan plot",
    short: "A theory that the aircraft went north and was hidden in Central Asia.",
    status: "Speculative",
    score: 1,
    claim:
      "Hijackers allegedly manipulated the satellite data and flew the aircraft north toward Kazakhstan or another Russian-linked location.",
    whyItSpread:
      "A northern corridor showed up in early maps, and suspicion of Russia made the theory feel like a spy story.",
    evidenceCheck:
      "The search logic, satellite data, and Indian Ocean debris all point away from a northern landing scenario.",
    verdict:
      "Very speculative and contradicted by debris evidence. It is useful to study as a media theory, not as the most likely explanation.",
    apush:
      "This connects to post-Cold War suspicion and how U.S.-Russia tensions can shape public explanations even when evidence is thin.",
    sources: ["atsb", "theweek"],
  },
  {
    id: "remote-control",
    title: "Remote-control hijack",
    short: "The idea that Boeing or another actor took over the plane electronically.",
    status: "Fringe",
    score: 1,
    claim:
      "A patented uninterruptible autopilot or remote-control system was used to seize MH370 and fly it somewhere else.",
    whyItSpread:
      "A real Boeing patent got mixed with post-9/11 fears about aircraft being used as weapons.",
    evidenceCheck:
      "Reporting on the final investigation notes Boeing told investigators the patented system was not implemented on any commercial aircraft, and MH370 was delivered before the patent.",
    verdict:
      "Creative, but unsupported. A real patent does not mean the system existed on MH370.",
    apush:
      "This is a classic modern technology panic: the public sees a real capability on paper and assumes a secret operational system.",
    sources: ["aviationtoday"],
  },
  {
    id: "shootdown",
    title: "U.S. shoot-down",
    short: "The claim that the U.S. military destroyed the aircraft and covered it up.",
    status: "Fringe",
    score: 0,
    claim:
      "The U.S. military allegedly shot down MH370 near the Maldives or Diego Garcia because it was thought to be a threat.",
    whyItSpread:
      "It combines a missing plane, a U.S. base, post-9/11 security anxiety, and the absence of a recovered fuselage.",
    evidenceCheck:
      "Public evidence does not show missiles, radar tracks, acoustic data, debris-field proof, or official confirmation for a shoot-down. Confirmed debris supports an Indian Ocean end rather than a known military intercept.",
    verdict:
      "There is no credible public evidence for it. It works better as an example of how uncertainty can turn into accusation.",
    apush:
      "The theory reflects public mistrust of U.S. military secrecy, especially after Iraq, Afghanistan, drones, and intelligence controversies.",
    sources: ["atsb", "theweek"],
  },
  {
    id: "phantom-phones",
    title: "Phantom cellphone rings",
    short: "Families heard ringing tones and hoped the passengers were alive.",
    status: "Speculative",
    score: 1,
    claim:
      "Because some phones appeared to ring when called, the aircraft must have landed and passengers might have survived.",
    whyItSpread:
      "It was emotionally powerful: in the absence of wreckage, a ringing tone felt like evidence of life.",
    evidenceCheck:
      "Telecom routing can create ringing tones before a phone is actually reached, especially before a call fails or goes to voicemail. A ringtone heard by the caller is not proof the handset is connected.",
    verdict:
      "Totally understandable, but weak as evidence. It belongs in the story because it shows how families experienced uncertainty in real time.",
    apush:
      "This turns technology into emotional evidence. The public read a network behavior as a historical clue because the official record was incomplete.",
    sources: ["guardian"],
  },
];

const timelineEvents: TimelineEvent[] = [
  {
    id: "departure",
    date: "March 8, 2014",
    time: "00:41 MYT",
    title: "MH370 departs Kuala Lumpur",
    filter: "flight",
    kicker: "Kuala Lumpur to Beijing",
    what: "Malaysia Airlines Flight 370, a Boeing 777-200ER carrying 239 passengers and crew, left Kuala Lumpur International Airport for Beijing.",
    matters:
      "The route was normal, which is part of why the case hit so hard: a routine global flight turned into proof that the modern world still cannot see everything.",
    apush:
      "For APUSH, this fits the post-Cold War world: Americans travel, trade, and communicate inside global systems whose failures can become international events.",
    source: "mot",
  },
  {
    id: "last-contact",
    date: "March 8, 2014",
    time: "01:19 MYT",
    title: "Final voice contact",
    filter: "flight",
    kicker: "Air traffic control handoff",
    what: "The last routine voice message came as MH370 moved between Malaysian and Vietnamese air traffic control sectors.",
    matters:
      "The handoff mattered because the plane became hard to track right as responsibility was moving between countries.",
    apush:
      "The event shows globalization's weak spots: modern transportation crosses borders faster than institutions can always coordinate.",
    source: "mot",
  },
  {
    id: "radar-loss",
    date: "March 8, 2014",
    time: "01:21 MYT",
    title: "Transponder signal disappears",
    filter: "flight",
    kicker: "Civil radar gap",
    what: "The aircraft stopped transmitting normal secondary-radar data, removing the easiest way civilian controllers identify a plane's position and altitude.",
    matters:
      "The loss showed something most passengers never think about: modern aviation still relies on planes broadcasting their own identity.",
    apush:
      "This is a technology-and-state-power issue. The U.S. and other countries had advanced surveillance tools, but no single state had perfect global visibility.",
    source: "mot",
  },
  {
    id: "military-radar",
    date: "March 8, 2014",
    time: "02:22 MYT",
    title: "Last primary-radar trace",
    filter: "flight",
    kicker: "Andaman Sea track",
    what: "Military radar data later indicated the aircraft had turned back across the Malay Peninsula and moved toward the Andaman Sea before disappearing from radar coverage.",
    matters:
      "This shifted attention away from the original route and forced investigators to piece together radar, satellite, and drift-model evidence.",
    apush:
      "The episode echoes a major modern-history theme: national-security tools can become crucial in civilian crises, especially in the Indo-Pacific region.",
    source: "mot",
  },
  {
    id: "satellite-handshakes",
    date: "March 8, 2014",
    time: "08:19 MYT",
    title: "Final satellite handshake",
    filter: "flight",
    kicker: "Data without a location",
    what: "Inmarsat satellite communications data showed automated connections, including a final signal that helped define a possible arc across the southern Indian Ocean.",
    matters:
      "The satellite data did not reveal an exact crash site. It gave investigators a rough search arc, which is why the search became so huge and difficult.",
    apush:
      "This is the information age at work: history was shaped by metadata, models, and uncertainty instead of a clear eyewitness record.",
    source: "atsb",
  },
  {
    id: "multinational-search",
    date: "March-April 2014",
    title: "Multinational surface search expands",
    filter: "search",
    kicker: "Ships, aircraft, satellites",
    what: "Search teams moved through different regions as evidence changed, eventually focusing on the southern Indian Ocean west of Australia.",
    matters:
      "The search became one of aviation's most expensive international efforts.",
    apush:
      "The United States participated through military assets and technical expertise, showing the reach of U.S. power in Pacific and Indian Ocean security networks.",
    source: "atsb",
  },
  {
    id: "us-p8",
    date: "April 2014",
    title: "U.S. Navy deploys P-8 Poseidon support",
    filter: "search",
    kicker: "American maritime surveillance",
    what: "The U.S. 7th Fleet added P-8 Poseidon maritime patrol aircraft to the search effort, pairing aircraft range and sensors with multinational coordination.",
    matters:
      "The U.S. did not run the investigation, but American aircraft and sensors helped search an enormous ocean region.",
    apush:
      "This connects MH370 to modern U.S. history: after World War II and the Cold War, the U.S. maintained a Pacific presence that could be used for humanitarian and safety crises.",
    source: "navy",
  },
  {
    id: "flaperon",
    date: "July 2015",
    title: "First confirmed debris appears",
    filter: "debris",
    kicker: "Reunion Island",
    what: "A wing part known as a flaperon washed ashore on Reunion Island and was later confirmed as coming from MH370.",
    matters:
      "The discovery proved the aircraft ended in the Indian Ocean, but debris did not reveal the main wreckage location.",
    apush:
      "It shows how evidence can travel through natural systems. Drift, currents, and time became part of the historical record.",
    source: "ap",
  },
  {
    id: "underwater-search",
    date: "2014-2017",
    title: "Large underwater search ends",
    filter: "search",
    kicker: "Seafloor mapping",
    what: "Australia-led search teams mapped and scanned large areas of the southern Indian Ocean using sonar and underwater search technology.",
    matters:
      "The search showed both the power and limits of modern technology: even detailed seafloor mapping could not guarantee a find in remote, deep water.",
    apush:
      "This connects to a broader historical theme: modern states use science and machines to reduce uncertainty, but nature still sets hard limits.",
    source: "atsb",
  },
  {
    id: "gadss",
    date: "2016 onward",
    title: "Aircraft tracking reform accelerates",
    filter: "policy",
    kicker: "ICAO and GADSS",
    what: "ICAO advanced global aircraft tracking and distress standards through the Global Aeronautical Distress and Safety System.",
    matters:
      "MH370 became a policy lesson: if a modern aircraft can vanish, tracking standards need to change before the next crisis.",
    apush:
      "This is Progressive Era logic in a modern form: a disaster exposes a system failure, then reformers push standards to make future systems safer.",
    source: "icao",
  },
  {
    id: "ocean-infinity-2018",
    date: "2018",
    title: "Ocean Infinity private search",
    filter: "search",
    kicker: "No-find, no-fee model",
    what: "Ocean Infinity searched a new area under a no-find, no-fee arrangement with Malaysia but did not locate the wreckage.",
    matters:
      "The model showed how private robotics companies entered a problem once mostly handled by governments.",
    apush:
      "It fits a modern U.S. economic theme: private technology firms increasingly work alongside governments in high-stakes public problems.",
    source: "ap",
  },
  {
    id: "search-2026",
    date: "March 8, 2026",
    title: "Renewed search update reports no confirmed wreckage",
    filter: "today",
    kicker: "Current status",
    what: "Malaysia's AAIB said the 2025/2026 Ocean Infinity search surveyed about 7,571 square kilometers after the agreement and had not confirmed the aircraft location.",
    matters:
      "Twelve years later, MH370 still does not have a clear ending. For the families, investigators, and aviation safety experts, it is not just an old news story.",
    apush:
      "The persistence of the search shows how public memory, grief, media pressure, and government responsibility continue long after a news cycle ends.",
    source: "mot2026",
  },
];

const evidenceCards = [
  {
    title: "Known",
    icon: Info,
    tone: "text-emerald-100/82 border-emerald-200/16 bg-emerald-200/[0.055]",
    items: [
      "MH370 carried 239 people on a Kuala Lumpur to Beijing route.",
      "The aircraft left its planned path and stopped normal transponder reporting.",
      "Satellite data supported a southern Indian Ocean search area.",
      "Debris confirmed the aircraft ended in the Indian Ocean.",
    ],
  },
  {
    title: "Still unknown",
    icon: ShieldAlert,
    tone: "text-amber-100/82 border-amber-200/18 bg-amber-200/[0.06]",
    items: [
      "The main wreckage location has not been confirmed.",
      "The cockpit voice recorder and flight data recorder have not been recovered.",
      "Investigators have not established a final cause.",
      "The timeline after the final radar trace depends on models and probabilities.",
    ],
  },
  {
    title: "Misleading",
    icon: Radio,
    tone: "text-red-100/76 border-red-200/16 bg-red-200/[0.05]",
    items: [
      "Missing evidence is not the same thing as proof of a conspiracy.",
      "Satellite arcs are not exact GPS tracks.",
      "Debris discoveries support an ocean crash, not a complete location.",
      "A strong project separates real sources from speculation.",
    ],
  },
];

const searchTech = [
  {
    title: "Primary and secondary radar",
    icon: Radar,
    body: "Secondary radar depends on aircraft transponder replies. Primary radar can see returns without a transponder, but range, geography, and military coverage matter.",
  },
  {
    title: "Satellite handshakes",
    icon: Satellite,
    body: "Automated satellite connections helped investigators estimate arcs. That was powerful, but it was still a model, not a pinpoint location.",
  },
  {
    title: "Pingers and time pressure",
    icon: Radio,
    body: "Black-box locator beacons have limited battery life, so early underwater detection was a race against time in one of the hardest oceans to search.",
  },
  {
    title: "Sonar and autonomous vessels",
    icon: Ship,
    body: "Search teams used seafloor mapping and underwater robotics to scan remote deep ocean. The problem was not only finding metal; it was knowing where to scan.",
  },
];

const apushThemes = [
  {
    title: "U.S. reach after the Cold War",
    body: "The U.S. did not control the investigation, but Navy aircraft and Pacific-based military infrastructure helped the search. That shows how American power in the Indo-Pacific still mattered after the Cold War.",
  },
  {
    title: "Globalization's fragile systems",
    body: "One flight connected Malaysia, China, Australia, Europe, the United States, and international aviation rules. The disappearance exposed how connected systems can still have gaps.",
  },
  {
    title: "The information age",
    body: "The public saw satellite metadata, maps, theories, leaks, and press conferences unfold in real time. MH370 became a case study in how people react when data exists but certainty does not.",
  },
  {
    title: "Reform after disaster",
    body: "Like earlier moments in U.S. history when tragedy led to regulation, MH370 pushed aviation authorities toward better tracking and distress standards.",
  },
];

const legacyItems = [
  "Families kept pressure on governments and companies to keep searching, turning grief into public accountability.",
  "Aviation safety moved toward better tracking expectations because a modern airliner disappearing was unacceptable.",
  "Search technology improved, but the case still shows that advanced systems depend on good assumptions.",
  "The story still matters because it mixes human loss, global institutions, U.S. power, private technology, and media uncertainty.",
];

function cx(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function RainCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const drops: Array<{ x: number; y: number; length: number; speed: number; alpha: number; drift: number }> = [];
    let width = window.innerWidth;
    let height = window.innerHeight;
    let animationFrame = 0;
    let lastTime = performance.now();
    let dpr = Math.min(window.devicePixelRatio || 1, 2);

    const resetDrop = (drop: (typeof drops)[number], randomY = false) => {
      drop.x = Math.random() * width;
      drop.y = randomY ? Math.random() * height : -40 - Math.random() * height * 0.25;
      drop.length = reducedMotion ? 8 + Math.random() * 8 : 18 + Math.random() * 30;
      drop.speed = reducedMotion ? 120 + Math.random() * 80 : 520 + Math.random() * 560;
      drop.alpha = reducedMotion ? 0.08 + Math.random() * 0.08 : 0.12 + Math.random() * 0.24;
      drop.drift = reducedMotion ? 20 + Math.random() * 24 : 90 + Math.random() * 110;
    };

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const targetCount = reducedMotion ? 60 : width < 760 ? 120 : 240;
      drops.length = 0;
      for (let i = 0; i < targetCount; i += 1) {
        const drop = { x: 0, y: 0, length: 0, speed: 0, alpha: 0, drift: 0 };
        resetDrop(drop, true);
        drops.push(drop);
      }
    };

    const draw = (now: number) => {
      const delta = Math.min((now - lastTime) / 1000, 0.034);
      lastTime = now;

      ctx.clearRect(0, 0, width, height);
      ctx.lineCap = "round";
      ctx.lineWidth = reducedMotion ? 0.75 : 1.1;

      for (const drop of drops) {
        drop.y += drop.speed * delta;
        drop.x += drop.drift * delta;
        if (drop.y > height + 80 || drop.x > width + 80) {
          resetDrop(drop);
        }

        ctx.strokeStyle = `rgba(170, 219, 236, ${drop.alpha})`;
        ctx.beginPath();
        ctx.moveTo(drop.x, drop.y);
        ctx.lineTo(drop.x - drop.drift * 0.045, drop.y + drop.length);
        ctx.stroke();
      }

      animationFrame = window.requestAnimationFrame(draw);
    };

    resize();
    window.addEventListener("resize", resize);
    animationFrame = window.requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", resize);
      window.cancelAnimationFrame(animationFrame);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-[2] opacity-55 mix-blend-screen"
    />
  );
}

function AnimatedBackdrop({ parallax }: { parallax: { x: number; y: number } }) {
  return (
    <div className="fixed inset-0 overflow-hidden bg-[#02070b]" aria-hidden="true">
      <div
        className="absolute inset-[-3%] overflow-hidden will-change-transform"
        style={{
          transform: `translate3d(${parallax.x * -10}px, ${parallax.y * -8}px, 0) scale(1.04)`,
        }}
      >
        <div className="absolute inset-0 bg-[linear-gradient(180deg,#091119_0%,#0c151c_38%,#050a0e_100%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(5,10,14,0.88),rgba(5,10,14,0.32)_45%,rgba(5,10,14,0.68)),radial-gradient(ellipse_at_74%_20%,rgba(196,213,215,0.13),transparent_27%),radial-gradient(ellipse_at_86%_58%,rgba(196,153,83,0.11),transparent_24%)]" />
        <div className="absolute left-[-12%] top-[-8%] h-[44vh] w-[124vw] bg-[radial-gradient(ellipse_at_18%_58%,rgba(16,28,36,0.82),transparent_34%),radial-gradient(ellipse_at_52%_38%,rgba(32,45,52,0.62),transparent_38%),radial-gradient(ellipse_at_78%_48%,rgba(43,52,56,0.52),transparent_34%)] opacity-85 mh370-cloud-drift" />
        <div className="absolute bottom-0 left-0 h-[42vh] w-full bg-[linear-gradient(180deg,rgba(2,7,11,0)_0%,rgba(4,11,14,0.74)_17%,#03070a_78%),repeating-linear-gradient(172deg,rgba(182,207,202,0.09)_0_1px,transparent_1px_24px),repeating-linear-gradient(8deg,rgba(255,255,255,0.04)_0_1px,transparent_1px_34px)] mh370-ocean" />
        <div className="absolute bottom-[29vh] left-0 h-px w-full bg-gradient-to-r from-transparent via-stone-200/14 to-transparent" />
      </div>
      <svg
        viewBox="0 0 760 220"
        className="absolute right-[-6rem] top-[18vh] h-auto w-[38rem] max-w-[80vw] text-stone-200/16 will-change-transform mh370-code-plane"
        style={{ transform: `translate3d(${parallax.x * -26}px, ${parallax.y * -16}px, 0)` }}
      >
        <path
          d="M64 126c98-42 221-66 358-73 53-3 93 2 122 16l122 60c9 4 11 16 3 22-17 13-46 16-82 7l-139-35-103 62c-17 10-37 15-57 14l-21-1 61-93-142-19-54 44c-14 11-32 17-50 17H47c-18 0-21-14 17-21Z"
          fill="rgba(231, 222, 201, 0.04)"
          stroke="currentColor"
          strokeWidth="3"
        />
        <path
          d="M455 54 322 7c-16-6-35-3-49 8l-17 14 111 37 88-12Z"
          fill="none"
          stroke="rgba(231, 222, 201, 0.12)"
          strokeWidth="3"
        />
        <path
          d="M71 132c128-32 282-42 456 0"
          fill="none"
          stroke="rgba(231, 222, 201, 0.13)"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(2,7,11,0.02),rgba(2,7,11,0.8)_68%,#02070b)]" />
      <div
        className="absolute left-[-18rem] top-[15vh] h-[44rem] w-[44rem] rounded-full border border-stone-200/8 opacity-60 will-change-transform mh370-radar"
        style={{ transform: `translate3d(${parallax.x * 18}px, ${parallax.y * 12}px, 0)` }}
      >
        <div className="absolute inset-[16%] rounded-full border border-stone-200/8" />
        <div className="absolute inset-[32%] rounded-full border border-stone-200/8" />
        <div className="absolute left-1/2 top-0 h-full w-px bg-stone-100/8" />
        <div className="absolute left-0 top-1/2 h-px w-full bg-stone-100/8" />
        <div className="absolute left-1/2 top-1/2 h-px w-1/2 origin-left bg-gradient-to-r from-emerald-200/28 to-transparent mh370-sweep" />
      </div>
      <div className="absolute inset-0 opacity-[0.055] [background-image:linear-gradient(rgba(255,255,255,0.28)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.28)_1px,transparent_1px)] [background-size:72px_72px]" />
      <div className="absolute left-[8%] top-[31%] hidden h-px w-[50vw] origin-left rotate-[-13deg] bg-gradient-to-r from-transparent via-emerald-200/28 to-amber-100/22 md:block mh370-route-line" />
      <RainCanvas />
    </div>
  );
}

function SourceLink({ sourceId }: { sourceId: SourceId }) {
  const source = sources[sourceId];
  return (
    <a
      href={source.href}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-2 rounded-sm border border-stone-200/14 bg-stone-200/[0.045] px-3 py-1.5 text-xs font-medium text-stone-200/72 transition hover:border-emerald-200/28 hover:bg-stone-200/[0.075] hover:text-stone-100"
    >
      {source.name}
      <ExternalLink className="h-3.5 w-3.5" />
    </a>
  );
}

function SourcePills({ sourceIds }: { sourceIds: SourceId[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {sourceIds.map((sourceId) => (
        <SourceLink key={sourceId} sourceId={sourceId} />
      ))}
    </div>
  );
}

function EvidenceMeter({ score }: { score: number }) {
  return (
    <div className="flex items-center gap-2" aria-label={`Evidence strength ${score} out of 5`}>
      {Array.from({ length: 5 }, (_, index) => (
        <span
          key={index}
          className={cx(
            "h-2.5 flex-1 rounded-sm border",
            index < score
              ? "border-amber-200/50 bg-amber-200/55"
              : "border-stone-200/16 bg-stone-200/[0.035]",
          )}
        />
      ))}
      <span className="ml-2 font-mono text-[11px] text-stone-300/58">{score}/5</span>
    </div>
  );
}

function SectionTitle({
  eyebrow,
  title,
  body,
}: {
  eyebrow: string;
  title: string;
  body: string;
}) {
  return (
    <div className="max-w-3xl">
      <div className="inline-flex items-center gap-2 border-l-2 border-amber-200/70 bg-stone-200/[0.045] px-3 py-1.5 font-mono text-[11px] font-medium uppercase tracking-normal text-stone-200/78">
        {eyebrow}
      </div>
      <h2 className="mt-4 text-3xl font-semibold tracking-normal text-stone-50 sm:text-4xl">{title}</h2>
      <p className="mt-3 text-base leading-7 text-stone-200/66 sm:text-lg">{body}</p>
    </div>
  );
}

function GlassPanel({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cx(
        "rounded-sm border border-stone-200/14 bg-[#071017]/88 shadow-[0_12px_34px_rgba(0,0,0,0.24)] backdrop-blur-md",
        className,
      )}
    >
      {children}
    </div>
  );
}

function StatBlock({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-sm border border-stone-200/14 bg-stone-200/[0.04] p-4">
      <div className="font-mono text-[11px] uppercase tracking-normal text-stone-300/54">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-stone-50">{value}</div>
      <div className="mt-2 text-sm leading-6 text-stone-300/62">{detail}</div>
    </div>
  );
}

function OverviewTab() {
  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_0.92fr]">
      <GlassPanel className="p-5 sm:p-6">
        <SectionTitle
          eyebrow="Main idea"
          title="MH370 became controversial because people never got a clear ending."
          body="A modern passenger jet disappeared, the main wreckage was not found, and the official answers still had gaps. That left room for theories to spread online and in the media."
        />
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <StatBlock label="People aboard" value="239" detail="227 passengers and 12 crew members." />
          <StatBlock label="Aircraft" value="Boeing 777" detail="A long-range jet built for global routes." />
          <StatBlock label="Route" value="KUL to PEK" detail="Kuala Lumpur to Beijing, a routine international flight." />
          <StatBlock label="Status" value="Still unknown" detail="No confirmed main wreckage location as of March 8, 2026." />
        </div>
      </GlassPanel>

      <GlassPanel className="overflow-hidden">
        <div className="border-b border-stone-200/12 p-5 sm:p-6">
          <div className="flex items-center gap-3 text-stone-50">
            <Compass className="h-5 w-5 text-amber-200/82" />
            <h3 className="text-xl font-semibold">Reader guide</h3>
          </div>
          <p className="mt-3 text-sm leading-7 text-stone-300/66">
            Use the tabs like an investigation board. The timeline explains what happened, Evidence separates facts from
            open questions, Search explains the technology, and APUSH connects the case to bigger historical themes.
          </p>
        </div>
        <div className="grid gap-3 p-5 sm:p-6">
          {[
            "The project talks about conspiracies, but it does not treat rumors as facts.",
            "It connects MH370 to media, technology, U.S. power, and global cooperation.",
            "It also keeps in mind that 239 real people were on the flight.",
          ].map((item) => (
            <div key={item} className="flex gap-3 rounded-sm border border-stone-200/10 bg-stone-200/[0.035] p-4">
              <ChevronRight className="mt-1 h-4 w-4 shrink-0 text-amber-200/70" />
              <p className="text-sm leading-6 text-stone-300/68">{item}</p>
            </div>
          ))}
        </div>
      </GlassPanel>
    </div>
  );
}

function ControversiesTab() {
  const [selectedId, setSelectedId] = useState(controversyCases[0].id);
  const [statusFilter, setStatusFilter] = useState<"all" | ControversyCase["status"]>("all");
  const selected = controversyCases.find((item) => item.id === selectedId) ?? controversyCases[0];
  const filtered = controversyCases.filter((item) => statusFilter === "all" || item.status === statusFilter);

  const chooseFilter = (nextFilter: "all" | ControversyCase["status"]) => {
    setStatusFilter(nextFilter);
    setSelectedId((current) => {
      const nextCases = controversyCases.filter((item) => nextFilter === "all" || item.status === nextFilter);
      return nextCases.some((item) => item.id === current) ? current : nextCases[0]?.id ?? controversyCases[0].id;
    });
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(24rem,1.1fr)]">
      <GlassPanel className="overflow-hidden">
        <div className="border-b border-stone-200/12 p-5">
          <div className="font-mono text-[11px] uppercase tracking-normal text-stone-300/56">Interactive claim board</div>
          <h2 className="mt-2 text-2xl font-semibold text-stone-50">Pick a theory and compare it with the evidence.</h2>
          <p className="mt-3 text-sm leading-7 text-stone-300/66">
            I am not saying every theory is equally believable. This section shows why some ideas are still discussed,
            and why others mostly survive because the wreckage and black boxes have not been found.
          </p>
        </div>

        <div className="grid gap-3 border-b border-stone-200/12 p-4 sm:grid-cols-3">
          {[
            ["0-1", "Mostly contradicted or unsupported"],
            ["2-3", "Possible, but missing proof"],
            ["4-5", "Strongly supported by public evidence"],
          ].map(([score, label]) => (
            <div key={score} className="rounded-sm border border-stone-200/10 bg-stone-200/[0.03] p-3">
              <div className="font-mono text-[11px] uppercase tracking-normal text-amber-100/60">{score}</div>
              <div className="mt-1 text-xs leading-5 text-stone-300/62">{label}</div>
            </div>
          ))}
        </div>

        <div className="border-b border-stone-200/12 p-4">
          <div className="flex flex-wrap gap-2">
            {(["all", "Serious theory", "Speculative", "Fringe"] as const).map((item) => (
              <button
                key={item}
                onClick={() => chooseFilter(item)}
                className={cx(
                  "rounded-sm border px-3 py-2 font-mono text-[11px] uppercase tracking-normal transition focus:outline-none focus:ring-2 focus:ring-amber-200/55",
                  statusFilter === item
                    ? "border-amber-200/42 bg-amber-200/[0.1] text-stone-50"
                    : "border-stone-200/12 bg-stone-200/[0.035] text-stone-300/62 hover:border-stone-200/22 hover:bg-stone-200/[0.06]",
                )}
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        <div className="grid gap-3 p-4">
          {filtered.map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedId(item.id)}
              className={cx(
                "rounded-sm border p-4 text-left transition focus:outline-none focus:ring-2 focus:ring-amber-200/55",
                item.id === selected.id
                  ? "border-amber-200/38 bg-amber-200/[0.075]"
                  : "border-stone-200/12 bg-stone-200/[0.032] hover:border-stone-200/22 hover:bg-stone-200/[0.055]",
              )}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="font-mono text-[11px] uppercase tracking-normal text-stone-300/50">{item.status}</div>
                  <h3 className="mt-2 text-lg font-semibold text-stone-50">{item.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-stone-300/64">{item.short}</p>
                </div>
                <ChevronRight
                  className={cx(
                    "mt-1 h-5 w-5 shrink-0 transition",
                    item.id === selected.id ? "translate-x-1 text-amber-100" : "text-stone-200/30",
                  )}
                />
              </div>
            </button>
          ))}
        </div>
      </GlassPanel>

      <GlassPanel className="h-fit overflow-hidden">
        <div className="border-b border-stone-200/12 bg-stone-200/[0.035] p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="font-mono text-[11px] uppercase tracking-normal text-amber-100/62">{selected.status}</div>
              <h2 className="mt-2 text-3xl font-semibold text-stone-50">{selected.title}</h2>
            </div>
            <div className="min-w-44">
              <div className="mb-2 font-mono text-[11px] uppercase tracking-normal text-stone-300/50">Evidence strength</div>
              <EvidenceMeter score={selected.score} />
            </div>
          </div>
        </div>

        <div className="grid gap-4 p-5">
          {[
            ["The claim", selected.claim],
            ["Why it spread", selected.whyItSpread],
            ["Evidence check", selected.evidenceCheck],
            ["Verdict", selected.verdict],
            ["APUSH connection", selected.apush],
          ].map(([label, body]) => (
            <div key={label} className="rounded-sm border border-stone-200/10 bg-stone-200/[0.032] p-4">
              <div className="font-mono text-[11px] uppercase tracking-normal text-stone-300/46">{label}</div>
              <p className="mt-2 text-sm leading-7 text-stone-300/70">{body}</p>
            </div>
          ))}
          <div className="rounded-sm border border-amber-200/18 bg-amber-200/[0.045] p-4">
            <div className="mb-3 font-mono text-[11px] uppercase tracking-normal text-amber-100/62">
              Sources for this card
            </div>
            <SourcePills sourceIds={selected.sources} />
          </div>
        </div>
      </GlassPanel>
    </div>
  );
}

function TimelineTab() {
  const [filter, setFilter] = useState<TimelineFilter>("all");
  const filteredEvents = useMemo(
    () => timelineEvents.filter((event) => filter === "all" || event.filter === filter),
    [filter],
  );
  const [selectedId, setSelectedId] = useState(filteredEvents[0]?.id ?? timelineEvents[0].id);
  const selected = timelineEvents.find((event) => event.id === selectedId) ?? filteredEvents[0] ?? timelineEvents[0];

  const selectFilter = (nextFilter: TimelineFilter) => {
    setFilter(nextFilter);
    setSelectedId((currentId) => {
      const nextEvents = timelineEvents.filter((event) => nextFilter === "all" || event.filter === nextFilter);
      return nextEvents.some((event) => event.id === currentId) ? currentId : nextEvents[0]?.id ?? timelineEvents[0].id;
    });
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_25rem]">
      <GlassPanel className="p-4 sm:p-5">
        <div className="flex flex-wrap gap-2">
          {filters.map((item) => (
            <button
              key={item.id}
              onClick={() => selectFilter(item.id)}
              className={cx(
                "rounded-sm border px-3 py-2 font-mono text-[12px] font-medium uppercase tracking-normal transition focus:outline-none focus:ring-2 focus:ring-amber-200/55",
                filter === item.id
                  ? "border-amber-200/45 bg-amber-200/[0.1] text-stone-50"
                  : "border-stone-200/12 bg-stone-200/[0.035] text-stone-300/62 hover:border-stone-200/22 hover:bg-stone-200/[0.06] hover:text-stone-100",
              )}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="mt-5 grid gap-3">
          {filteredEvents.map((event) => (
            <button
              key={event.id}
              onClick={() => setSelectedId(event.id)}
              className={cx(
                "group rounded-sm border p-4 text-left transition duration-300 focus:outline-none focus:ring-2 focus:ring-amber-200/55",
                selected.id === event.id
                  ? "border-amber-200/36 bg-amber-200/[0.07]"
                  : "border-stone-200/12 bg-stone-200/[0.032] hover:border-stone-200/20 hover:bg-stone-200/[0.055]",
              )}
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2 font-mono text-[11px] font-medium uppercase tracking-normal text-stone-300/62">
                    <span>{event.date}</span>
                    {event.time ? <span className="rounded-sm bg-stone-200/8 px-2 py-0.5">{event.time}</span> : null}
                  </div>
                  <h3 className="mt-2 text-lg font-semibold text-stone-50">{event.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-stone-300/62">{event.kicker}</p>
                </div>
                <ChevronRight
                  className={cx(
                    "h-5 w-5 shrink-0 transition",
                    selected.id === event.id ? "translate-x-1 text-amber-100" : "text-stone-200/30 group-hover:text-stone-200/64",
                  )}
                />
              </div>
            </button>
          ))}
        </div>
      </GlassPanel>

      <GlassPanel className="h-fit overflow-hidden">
        <div className="border-b border-stone-200/12 bg-stone-200/[0.035] p-5">
          <div className="font-mono text-[11px] uppercase tracking-normal text-amber-100/62">{selected.date}</div>
          <h3 className="mt-2 text-2xl font-semibold text-stone-50">{selected.title}</h3>
          <div className="mt-4">
            <SourceLink sourceId={selected.source} />
          </div>
        </div>
        <div className="grid gap-4 p-5">
          {[
            ["What happened", selected.what],
            ["Why it mattered", selected.matters],
            ["APUSH connection", selected.apush],
          ].map(([title, body]) => (
            <div key={title} className="rounded-sm border border-stone-200/10 bg-stone-200/[0.032] p-4">
              <div className="font-mono text-[11px] uppercase tracking-normal text-stone-300/46">{title}</div>
              <p className="mt-2 text-sm leading-7 text-stone-300/68">{body}</p>
            </div>
          ))}
        </div>
      </GlassPanel>
    </div>
  );
}

function EvidenceTab() {
  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {evidenceCards.map((card) => {
        const Icon = card.icon;
        return (
          <GlassPanel key={card.title} className="overflow-hidden">
            <div className={cx("flex items-center gap-3 border-b p-5", card.tone)}>
              <Icon className="h-5 w-5" />
              <h3 className="text-xl font-semibold text-stone-50">{card.title}</h3>
            </div>
            <div className="grid gap-3 p-5">
              {card.items.map((item) => (
                <div key={item} className="rounded-sm border border-stone-200/10 bg-stone-200/[0.032] p-4 text-sm leading-7 text-stone-300/68">
                  {item}
                </div>
              ))}
            </div>
          </GlassPanel>
        );
      })}
    </div>
  );
}

function SearchTab() {
  return (
    <div className="grid gap-5">
      <GlassPanel className="p-5 sm:p-6">
        <SectionTitle
          eyebrow="Search technology"
          title="The hard part was not caring enough to search. It was knowing where the ocean floor mattered."
          body="MH370 forced investigators to combine weak signals: radar traces, satellite timing, black-box battery limits, drift models, sonar passes, and weather windows."
        />
      </GlassPanel>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {searchTech.map((item) => {
          const Icon = item.icon;
          return (
            <GlassPanel key={item.title} className="p-5">
              <div className="flex h-10 w-10 items-center justify-center rounded-sm border border-emerald-200/18 bg-emerald-200/[0.07] text-emerald-100/82">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-stone-50">{item.title}</h3>
              <p className="mt-3 text-sm leading-7 text-stone-300/64">{item.body}</p>
            </GlassPanel>
          );
        })}
      </div>
      <GlassPanel className="p-5 sm:p-6">
        <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <div className="font-mono text-[11px] uppercase tracking-normal text-stone-300/56">Why the Indian Ocean was brutal</div>
            <h3 className="mt-3 text-2xl font-semibold text-stone-50">Deep water, remote weather, and a moving probability map</h3>
          </div>
          <p className="text-sm leading-7 text-stone-300/66">
            Investigators were searching a changing idea of a place, not a known crash site. The southern Indian Ocean is vast,
            deep, and far from ports. Weather shortened operating windows, and every model depended on assumptions about fuel,
            flight path, drift, and impact.
          </p>
        </div>
      </GlassPanel>
    </div>
  );
}

function ApushTab() {
  return (
    <div className="grid gap-5">
      <GlassPanel className="p-5 sm:p-6">
        <SectionTitle
          eyebrow="Historical framing"
          title="The APUSH angle is not that MH370 was an American event. It is that America was part of the global system around it."
          body="MH370 belongs in a modern-history conversation about U.S. power, globalization, media, transportation, regulation, and public trust."
        />
      </GlassPanel>
      <div className="grid gap-4 md:grid-cols-2">
        {apushThemes.map((theme) => (
          <GlassPanel key={theme.title} className="p-5">
            <h3 className="text-xl font-semibold text-stone-50">{theme.title}</h3>
            <p className="mt-3 text-sm leading-7 text-stone-300/66">{theme.body}</p>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
}

function LegacyTab() {
  return (
    <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
      <GlassPanel className="p-5 sm:p-6">
        <SectionTitle
          eyebrow="Legacy"
          title="The unanswered question became a policy question."
          body="MH370 changed how people talked about global tracking. It also showed that grief can keep a public investigation alive for years."
        />
        <div className="mt-5 flex flex-wrap gap-2">
          <SourceLink sourceId="icao" />
          <SourceLink sourceId="mot2026" />
        </div>
      </GlassPanel>
      <div className="grid gap-3">
        {legacyItems.map((item, index) => (
          <GlassPanel key={item} className="p-4">
            <div className="flex gap-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-sm border border-amber-200/18 bg-amber-200/[0.08] font-mono text-sm font-semibold text-amber-100">
                {index + 1}
              </div>
              <p className="text-sm leading-7 text-stone-300/68">{item}</p>
            </div>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
}

function SourcesTab() {
  return (
    <div className="grid gap-5">
      <GlassPanel className="p-5 sm:p-6">
        <SectionTitle
          eyebrow="Works cited"
          title="Sources are shown on each controversy card and collected here."
          body="Official sources are used for facts about the search, debris, and investigation. Media sources are used mainly for public theories, early confusion, and controversy context."
        />
      </GlassPanel>
      <div className="grid gap-4 md:grid-cols-2">
        {Object.values(sources).map((source) => (
          <a
            key={source.id}
            href={source.href}
            target="_blank"
            rel="noreferrer"
            className="group rounded-sm border border-stone-200/14 bg-[#071017]/88 p-5 shadow-[0_12px_34px_rgba(0,0,0,0.2)] backdrop-blur-md transition hover:border-amber-200/28 hover:bg-stone-200/[0.045] focus:outline-none focus:ring-2 focus:ring-amber-200/55"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-normal text-stone-300/54">{source.name}</div>
                <h3 className="mt-3 text-xl font-semibold text-stone-50">{source.label}</h3>
              </div>
              <ExternalLink className="h-5 w-5 shrink-0 text-stone-200/38 transition group-hover:text-amber-100" />
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

function ActiveTabContent({ activeTab }: { activeTab: TabId }) {
  if (activeTab === "controversies") return <ControversiesTab />;
  if (activeTab === "timeline") return <TimelineTab />;
  if (activeTab === "evidence") return <EvidenceTab />;
  if (activeTab === "search") return <SearchTab />;
  if (activeTab === "apush") return <ApushTab />;
  if (activeTab === "legacy") return <LegacyTab />;
  if (activeTab === "sources") return <SourcesTab />;
  return <OverviewTab />;
}

export default function MH370Experience() {
  const [activeTab, setActiveTab] = useState<TabId>("controversies");
  const [parallax, setParallax] = useState({ x: 0, y: 0 });
  const parallaxFrame = useRef<number | null>(null);

  const activeIndex = tabs.findIndex((tab) => tab.id === activeTab);

  const handleTabKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    const nextIndex =
      event.key === "ArrowRight" ? (index + 1) % tabs.length : (index - 1 + tabs.length) % tabs.length;
    setActiveTab(tabs[nextIndex].id);
  };

  const handlePointerMove = (event: PointerEvent<HTMLElement>) => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || window.innerWidth < 768) return;
    const next = {
      x: (event.clientX / window.innerWidth - 0.5) * 2,
      y: (event.clientY / window.innerHeight - 0.5) * 2,
    };

    if (parallaxFrame.current) return;
    parallaxFrame.current = window.requestAnimationFrame(() => {
      setParallax(next);
      parallaxFrame.current = null;
    });
  };

  useEffect(() => {
    return () => {
      if (parallaxFrame.current) window.cancelAnimationFrame(parallaxFrame.current);
    };
  }, []);

  return (
    <main
      className="relative min-h-screen overflow-x-hidden bg-[#02070b] text-stone-50"
      onPointerMove={handlePointerMove}
    >
      <AnimatedBackdrop parallax={parallax} />

      <div className="relative z-10">
        <header className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 pb-8 pt-4 sm:px-6 lg:px-8">
          <nav className="flex flex-wrap items-center justify-between gap-3 rounded-sm border border-stone-200/14 bg-[#061017]/82 p-2 shadow-[0_12px_34px_rgba(0,0,0,0.22)] backdrop-blur-md">
            <div className="inline-flex items-center gap-2 rounded-sm px-3 py-2 text-sm font-medium text-stone-300/82">
              <Plane className="h-4 w-4" />
              Pushpak Jain & Akshaj Chityala
            </div>
            <div className="rounded-sm border border-stone-200/12 bg-stone-200/[0.035] px-3 py-2 font-mono text-[11px] uppercase tracking-normal text-stone-300/58">
              APUSH project
            </div>
          </nav>

          <section className="grid flex-1 items-end gap-6 py-10 lg:grid-cols-[minmax(0,1fr)_24rem] lg:py-14">
            <div className="max-w-4xl">
              <div className="inline-flex items-center gap-2 border-l-2 border-amber-200/70 bg-stone-200/[0.05] px-3 py-2 font-mono text-[11px] font-medium uppercase tracking-normal text-stone-200/78">
                MH370 research project
              </div>
              <h1 className="mt-6 max-w-4xl text-[3rem] font-semibold leading-[0.94] tracking-normal text-stone-50 sm:text-[4.8rem] lg:text-[6.2rem]">
                MH370: Theories and Evidence
              </h1>
              <p className="mt-5 max-w-3xl text-2xl font-medium leading-tight text-stone-100/92 sm:text-3xl">
                What people claimed, what evidence says, and why the case still matters.
              </p>
              <p className="mt-5 max-w-2xl text-base leading-8 text-stone-300/72 sm:text-lg">
                This project looks at the major theories around Malaysia Airlines Flight 370. Some are possible, some are
                weak, and some are basically internet rumors. The goal is to compare each claim with real evidence.
              </p>
              <div className="mt-7 grid max-w-3xl gap-2 border-l border-stone-200/18 pl-4 font-mono text-[11px] uppercase tracking-normal text-stone-300/56 sm:grid-cols-3 sm:border-l-0 sm:pl-0">
                <span>opened: 08 mar 2014</span>
                <span>route: kul to pek</span>
                <span>cause: undetermined</span>
              </div>
            </div>

            <GlassPanel className="p-5">
              <div className="flex items-center gap-3">
                <Waves className="h-5 w-5 text-emerald-100/78" />
                <h2 className="text-lg font-semibold text-stone-50">Investigation snapshot</h2>
              </div>
              <div className="mt-5 grid gap-3">
                {[
                  ["Aircraft", "Boeing 777-200ER"],
                  ["Route", "Kuala Lumpur to Beijing"],
                  ["Aboard", "239 people"],
                  ["Cause", "Undetermined"],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between gap-4 rounded-sm border border-stone-200/10 bg-stone-200/[0.035] px-4 py-3">
                    <span className="font-mono text-[11px] uppercase tracking-normal text-stone-300/46">{label}</span>
                    <span className="text-sm font-medium text-stone-100/84">{value}</span>
                  </div>
                ))}
              </div>
            </GlassPanel>
          </section>
        </header>

        <section className="mx-auto max-w-7xl px-4 pb-20 sm:px-6 lg:px-8">
          <div className="sticky top-3 z-30 rounded-sm border border-stone-200/14 bg-[#061017]/88 p-2 shadow-[0_12px_34px_rgba(0,0,0,0.28)] backdrop-blur-md">
            <div
              role="tablist"
              aria-label="MH370 project sections"
              className="flex gap-2 overflow-x-auto pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
            >
              {tabs.map((tab, index) => {
                const Icon = tab.icon;
                const selected = tab.id === activeTab;
                return (
                  <button
                    key={tab.id}
                    id={`mh370-tab-${tab.id}`}
                    type="button"
                    role="tab"
                    aria-selected={selected}
                    aria-controls={`mh370-panel-${tab.id}`}
                    tabIndex={selected ? 0 : -1}
                    onClick={() => setActiveTab(tab.id)}
                    onKeyDown={(event) => handleTabKeyDown(event, index)}
                    className={cx(
                      "inline-flex shrink-0 items-center gap-2 rounded-sm border px-3.5 py-2.5 text-sm font-medium transition duration-300 focus:outline-none focus:ring-2 focus:ring-amber-200/55",
                      selected
                        ? "border-amber-200/38 bg-amber-200/[0.09] text-stone-50"
                        : "border-stone-200/10 bg-stone-200/[0.032] text-stone-300/58 hover:border-stone-200/18 hover:bg-stone-200/[0.055] hover:text-stone-100",
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div
            id={`mh370-panel-${activeTab}`}
            role="tabpanel"
            aria-labelledby={`mh370-tab-${activeTab}`}
            className="mt-5 mh370-panel"
            key={activeTab}
            style={{ "--tab-index": activeIndex } as CSSProperties}
          >
            <ActiveTabContent activeTab={activeTab} />
          </div>
        </section>
      </div>

      <style jsx global>{`
        .mh370-sweep {
          animation: mh370Sweep 6.5s linear infinite;
          will-change: transform;
        }

        .mh370-route-line {
          animation: mh370RoutePulse 4.8s ease-in-out infinite;
          will-change: opacity, transform;
        }

        .mh370-panel {
          animation: mh370PanelIn 420ms cubic-bezier(0.22, 1, 0.36, 1) both;
          will-change: opacity, transform;
        }

        .mh370-cloud-drift {
          animation: mh370CloudDrift 18s ease-in-out infinite;
          will-change: opacity, background-position;
        }

        .mh370-ocean {
          animation: mh370OceanShift 9s linear infinite;
          will-change: background-position;
        }

        .mh370-code-plane {
          animation: mh370PlaneLight 5.6s ease-in-out infinite;
          will-change: opacity, filter, transform;
        }

        @keyframes mh370Sweep {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes mh370RoutePulse {
          0%,
          100% {
            opacity: 0.38;
            transform: rotate(-13deg) scaleX(0.96);
          }
          50% {
            opacity: 0.82;
            transform: rotate(-13deg) scaleX(1.03);
          }
        }

        @keyframes mh370PanelIn {
          from {
            opacity: 0;
            transform: translate3d(0, 14px, 0);
          }
          to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
          }
        }

        @keyframes mh370CloudDrift {
          0%,
          100% {
            opacity: 0.9;
            background-position: 0 0, 0 0, 0 0;
          }
          50% {
            opacity: 1;
            background-position: 28px 0, -22px 8px, 18px -6px;
          }
        }

        @keyframes mh370OceanShift {
          from {
            background-position: 0 0, 0 0, 0 0;
          }
          to {
            background-position: 0 0, 84px 0, -72px 0;
          }
        }

        @keyframes mh370PlaneLight {
          0%,
          100% {
            opacity: 0.66;
            filter: brightness(0.86);
          }
          50% {
            opacity: 0.78;
            filter: brightness(1.08);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .mh370-sweep,
          .mh370-route-line,
          .mh370-panel,
          .mh370-cloud-drift,
          .mh370-ocean,
          .mh370-code-plane {
            animation: none !important;
          }
        }
      `}</style>
    </main>
  );
}
