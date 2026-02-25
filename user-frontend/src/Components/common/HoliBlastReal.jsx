import { motion } from "framer-motion";

export default function HoliBlastReal() {
    return (
        <div className="fixed inset-0 overflow-hidden bg-neutral-900/60 z-[9999] pointer-events-none">

            {/* Pink Powder */}
            <motion.div
                initial={{ scale: 0.2, opacity: 0 }}
                animate={{ scale: 3, opacity: 0.9 }}
                transition={{ duration: 3, ease: "easeOut" }}
                className="absolute inset-0 mix-blend-screen"
            >
                <svg viewBox="0 0 600 600" className="w-full h-full">
                    <defs>
                        <radialGradient id="pinkGrad">
                            <stop offset="0%" stopColor="#ff4d6d" />
                            <stop offset="60%" stopColor="#ff4d6d" stopOpacity="0.6" />
                            <stop offset="100%" stopColor="transparent" />
                        </radialGradient>
                    </defs>
                    <path
                        d="M300,100 C400,50 550,200 500,350 C450,500 250,550 150,450 C50,350 100,200 300,100Z"
                        fill="url(#pinkGrad)"
                    />
                </svg>
            </motion.div>

            {/* Yellow Powder */}
            <motion.div
                initial={{ scale: 0.2, opacity: 0 }}
                animate={{ scale: 3, opacity: 0.8 }}
                transition={{ duration: 3, delay: 0.3, ease: "easeOut" }}
                className="absolute inset-0 mix-blend-screen"
            >
                <svg viewBox="0 0 600 600" className="w-full h-full">
                    <defs>
                        <radialGradient id="yellowGrad">
                            <stop offset="0%" stopColor="#ffd93d" />
                            <stop offset="60%" stopColor="#ffd93d" stopOpacity="0.6" />
                            <stop offset="100%" stopColor="transparent" />
                        </radialGradient>
                    </defs>
                    <path
                        d="M200,150 C350,50 600,250 450,450 C350,600 100,550 80,350 C50,250 100,200 200,150Z"
                        fill="url(#yellowGrad)"
                    />
                </svg>
            </motion.div>

            {/* Blue Powder */}
            <motion.div
                initial={{ scale: 0.2, opacity: 0 }}
                animate={{ scale: 3, opacity: 0.8 }}
                transition={{ duration: 3, delay: 0.6, ease: "easeOut" }}
                className="absolute inset-0 mix-blend-screen"
            >
                <svg viewBox="0 0 600 600" className="w-full h-full">
                    <defs>
                        <radialGradient id="blueGrad">
                            <stop offset="0%" stopColor="#4d96ff" />
                            <stop offset="60%" stopColor="#4d96ff" stopOpacity="0.6" />
                            <stop offset="100%" stopColor="transparent" />
                        </radialGradient>
                    </defs>
                    <path
                        d="M350,200 C550,150 650,400 500,550 C350,650 150,550 200,400 C250,300 250,250 350,200Z"
                        fill="url(#blueGrad)"
                    />
                </svg>
            </motion.div>

        </div>
    );
}
