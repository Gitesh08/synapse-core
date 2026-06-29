"use client";

import { motion } from "framer-motion";

function GithubIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  );
}

function LinkedinIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
      <rect x="2" y="9" width="4" height="12" />
      <circle cx="4" cy="4" r="2" />
    </svg>
  );
}

const team = [
  { 
    name: "Vinay Ghate", 
    title: "Cognitive Architect",
    image: "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=400&auto=format&fit=crop"
  },
  { 
    name: "Gitesh Mahadik", 
    title: "Infrastructure Lead",
    image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=400&auto=format&fit=crop"
  },
  { 
    name: "Shruti Birari", 
    title: "Data Modeling",
    image: "https://images.unsplash.com/photo-1604871000636-074fa5117945?q=80&w=400&auto=format&fit=crop"
  },
];

export function TeamSection() {
  return (
    <div className="w-full max-w-5xl mx-auto pt-24 pb-32 px-6 relative z-10 font-sans">
      <div className="text-center mb-16">
        <h2 className="text-2xl md:text-3xl font-semibold text-white tracking-tighter mb-3">
          The Architects
        </h2>
        <p className="text-[#888888] font-normal text-sm">
          Constructing the biological memory pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {team.map((member) => (
          <motion.div
            key={member.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="group relative"
          >
            <div className="relative flex flex-col bg-transparent border border-[#333333] rounded-none group-hover:border-white transition-colors duration-300 overflow-hidden h-full">
              
              {/* Image Container */}
              <div className="w-full aspect-square overflow-hidden bg-[#111111] border-b border-[#333333] group-hover:border-white transition-colors duration-300">
                {/* Using standard img to avoid next/image setup overhead, just for rapid prototyping */}
                <img 
                  src={member.image} 
                  alt={member.name}
                  className="w-full h-full object-cover grayscale contrast-[1.2] group-hover:grayscale-0 transition-all duration-500"
                />
              </div>

              {/* Typography / Footer */}
              <div className="p-5 flex flex-col justify-between flex-1">
                <div>
                  <h3 className="text-lg font-bold text-white tracking-tight">
                    {member.name}
                  </h3>
                  <p className="text-[10px] text-[#888888] font-medium mt-1 uppercase tracking-widest">
                    {member.title}
                  </p>
                </div>

                {/* Socials */}
                <div className="flex items-center justify-end gap-3 mt-6">
                  <a 
                    href="#" 
                    className="text-[#A1A1AA] hover:text-white transition-colors duration-300"
                  >
                    <GithubIcon />
                  </a>
                  <a 
                    href="#" 
                    className="text-[#A1A1AA] hover:text-white transition-colors duration-300"
                  >
                    <LinkedinIcon />
                  </a>
                </div>
              </div>

            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
