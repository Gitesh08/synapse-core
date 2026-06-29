import { ValenceMatrix } from "@/components/ValenceMatrix";
import { CodePlayground } from "@/components/CodePlayground";
import { CognitivePipeline } from "@/components/CognitivePipeline";
import { TeamSection } from "@/components/TeamSection";
import { HeroSimulation } from "@/components/HeroSimulation";
import { FAQSection } from "@/components/FAQSection";

export default function Home() {
  return (
    <main className="flex-1 flex flex-col relative overflow-hidden bg-black min-h-[calc(100vh-5rem)]">
      {/* Hero & Live Simulation Hook */}
      <HeroSimulation />

      {/* Feature Sections */}
      <div className="flex flex-col gap-12 pb-12 relative z-10 mt-12">
        <CognitivePipeline />
        <ValenceMatrix />
        <CodePlayground />
      </div>

      <FAQSection />

      {/* Footer / Team Section */}
      <TeamSection />
    </main>
  );
}
