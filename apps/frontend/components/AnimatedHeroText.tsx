"use client";

import { motion } from "framer-motion";

export function AnimatedHeroText() {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.3,
      },
    },
  };

  const lineVariants = {
    hidden: { opacity: 0, y: 30 },
    show: { opacity: 1, y: 0, transition: { duration: 1.2, ease: [0.16, 1, 0.3, 1] as const } },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="max-w-4xl mx-auto text-center z-10 relative"
    >
      <motion.h1
        variants={lineVariants}
        className="text-5xl md:text-7xl font-serif font-medium tracking-tight text-[#F8FAFC] mb-6 leading-[1.1]"
      >
        The AI Memory Engine <br className="hidden md:block" />
        <span className="text-[#E2B875] italic font-light">
          That Learns How to Forget
        </span>
      </motion.h1>

      <motion.p
        variants={lineVariants}
        className="text-lg md:text-xl text-[#94A3B8] mb-12 max-w-2xl mx-auto font-sans font-light leading-relaxed tracking-wide"
      >
        Veda-Mem brings dynamic context pruning and neural plasticity to your
        data infrastructure. Scale your AI memory organically, without the noise.
      </motion.p>
    </motion.div>
  );
}
