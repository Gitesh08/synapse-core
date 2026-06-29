"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { HardDrive, Filter, Database, Zap } from "lucide-react";

const pipelineSteps = [
  {
    id: 1,
    title: "Ingestion Buffer",
    subtitle: "Capturing the raw input.",
    desc: "User prompts are temporarily held before entering deep storage.",
    icon: HardDrive,
  },
  {
    id: 2,
    title: "Cognitive Evaluator",
    subtitle: "Filtering the noise.",
    desc: "An SLM evaluates the semantic importance of the input, assigning a strict 1-to-5 Significance Score.",
    icon: Filter,
  },
  {
    id: 3,
    title: "Decaying Graph Storage",
    subtitle: "The self-cleaning database.",
    desc: "Data enters the Cognee vector graph. Instead of permanent storage, unreferenced and trivial data naturally evaporates over time.",
    icon: Database,
  },
  {
    id: 4,
    title: "Instinct Consolidation",
    subtitle: "Compressing habits.",
    desc: "Dense clusters of historical data are permanently compressed into lightweight behavioral rules, bypassing token bloat.",
    icon: Zap,
  },
];

export function CognitivePipeline() {
  const containerRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start center", "end center"],
  });

  const lineHeight = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);

  return (
    <div className="w-full max-w-3xl mx-auto py-24 px-6 relative font-sans" ref={containerRef}>
      <div className="text-center mb-24">
        <h2 className="text-3xl md:text-5xl font-semibold text-white tracking-tighter mb-4">
          Data Pipeline
        </h2>
        <p className="text-[#888888] font-normal">
          How data flows through the architecture.
        </p>
      </div>

      <div className="relative">
        {/* The Vertical Connecting Line */}
        <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-px bg-[#333333] md:-translate-x-1/2" />
        
        {/* The Animated Fill Line */}
        <motion.div 
          className="absolute left-6 md:left-1/2 top-0 w-px bg-white md:-translate-x-1/2 origin-top"
          style={{ height: lineHeight }}
        />

        <div className="flex flex-col gap-12 md:gap-20">
          {pipelineSteps.map((step, index) => {
            const isEven = index % 2 === 0;
            const Icon = step.icon;

            return (
              <div 
                key={step.id}
                className="relative flex items-center md:justify-between flex-col md:flex-row gap-6 md:gap-0"
              >
                {/* Center Node on the line */}
                <div className="absolute left-6 md:left-1/2 top-4 md:top-1/2 -translate-x-1/2 md:-translate-y-1/2 z-10">
                  <div className="w-4 h-4 rounded-full border-2 border-black bg-white" />
                </div>

                {/* Content */}
                <div className={`w-full md:w-[45%] pl-16 md:pl-0 ${isEven ? 'md:text-right md:pr-12' : 'md:order-2 md:pl-12'}`}>
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-50px" }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="flex flex-col gap-2"
                  >
                    <div className={`flex items-center gap-3 ${isEven ? 'md:flex-row-reverse' : ''}`}>
                      <div className="w-8 h-8 rounded border border-[#333333] bg-[#0A0A0A] flex items-center justify-center">
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                      <h3 className="text-white font-medium text-lg tracking-tight">
                        {step.title}
                      </h3>
                    </div>
                    <span className="text-sm font-medium text-white block mt-2">
                      {step.subtitle}
                    </span>
                    <p className="text-[#888888] text-sm leading-relaxed font-normal">
                      {step.desc}
                    </p>
                  </motion.div>
                </div>

                {/* Empty Space for alignment */}
                <div className={`hidden md:block w-[45%] ${isEven ? 'order-2' : ''}`} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
