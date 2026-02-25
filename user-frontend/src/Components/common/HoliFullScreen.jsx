import { motion } from "framer-motion";

export default function HoliFullScreen() {
    return (
        <div className="fixed inset-0 w-full h-full overflow-hidden bg-neutral-900/40 pointer-events-none z-[9998]">

            {/* Pink Layer */}
            <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 2.5, opacity: 0.9 }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="absolute inset-0"
                style={{
                    background:
                        "radial-gradient(circle at 30% 40%, rgba(255,94,120,0.8) 0%, transparent 60%)",
                    filter: "blur(80px)",
                }}
            />

            {/* Yellow Layer */}
            <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 2.5, opacity: 0.8 }}
                transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
                className="absolute inset-0"
                style={{
                    background:
                        "radial-gradient(circle at 70% 30%, rgba(255,217,61,0.8) 0%, transparent 60%)",
                    filter: "blur(90px)",
                }}
            />

            {/* Blue Layer */}
            <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 2.5, opacity: 0.8 }}
                transition={{ duration: 1, delay: 1, ease: "easeOut" }}
                className="absolute inset-0"
                style={{
                    background:
                        "radial-gradient(circle at 50% 70%, rgba(94,194,247,0.8) 0%, transparent 60%)",
                    filter: "blur(100px)",
                }}
            />

            {/* Green Layer */}
            <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 2.5, opacity: 0.8 }}
                transition={{ duration: 1, delay: 1.5, ease: "easeOut" }}
                className="absolute inset-0"
                style={{
                    background:
                        "radial-gradient(circle at 20% 80%, rgba(123,211,137,0.8) 0%, transparent 60%)",
                    filter: "blur(100px)",
                }}
            />

        </div>
    );
}
