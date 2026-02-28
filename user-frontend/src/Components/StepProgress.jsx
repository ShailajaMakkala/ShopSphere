import React from "react";
import { Check } from "lucide-react";
import { useLocation } from "react-router-dom";
import { motion } from "framer-motion";

/**
 * Step definitions
 */
const steps = [
    {
        title: "Account verification",
        routes: ["/account-verification", "/verify-otp"],
    },
    {
        title: "Verify Tax Details",
        routes: ["/verifyGST", "/verifyPAN"],
    },
    {
        title: "Store Name",
        routes: ["/store-name"],
    },
    {
        title: "Shipping & Pickup",
        routes: [
            "/shipping-address",
            "/shipping-method",
            "/shipping-fee-preferences",
        ],
    },
    {
        title: "Bank Details",
        routes: ["/bank-details"],
    },
];

export default function StepProgress() {
    const location = useLocation();
    const currentPath = location.pathname;

    let currentStepIndex = steps.findIndex(step =>
        step.routes.some(route => currentPath.startsWith(route))
    );

    if (currentPath.startsWith("/account-verification") || currentPath.startsWith("/verify-otp")) {
        currentStepIndex = 0;
    }

    if (currentStepIndex === -1) currentStepIndex = 0;

    return (
        <div className="w-full max-w-4xl mx-auto mb-12 px-2 sm:px-4">
            <div className="flex items-start justify-between relative">
                {steps.map((step, index) => {
                    const isCompleted = index < currentStepIndex;
                    const isActive = index === currentStepIndex;

                    return (
                        <div
                            key={step.title}
                            className={`flex-1 relative ${index === steps.length - 1 ? "flex-none" : ""}`}
                        >
                            {/* Connector Line (except for last step) */}
                            {index < steps.length - 1 && (
                                <div className="absolute top-5 left-[50%] right-[-50%] h-[2px] bg-orange-100 z-0 overflow-hidden">
                                    <motion.div
                                        initial={{ width: "0%" }}
                                        animate={{ width: isCompleted ? "100%" : "0%" }}
                                        transition={{ duration: 0.8, ease: "easeInOut" }}
                                        className="h-full bg-gradient-to-r from-orange-400 to-purple-500"
                                    />
                                </div>
                            )}

                            {/* Step Item */}
                            <div className="relative flex flex-col items-center z-10">
                                {/* Circle */}
                                <motion.div
                                    initial={false}
                                    animate={{
                                        backgroundColor: isCompleted || isActive ? "#fb923c" : "#ffffff",
                                        borderColor: isCompleted || isActive ? "#fb923c" : "#fed7aa",
                                        scale: isActive ? 1.15 : 1,
                                    }}
                                    className={`flex items-center justify-center w-10 h-10 rounded-full border-2 shadow-sm transition-all duration-300
                                        ${isCompleted || isActive ? "text-white shadow-orange-400/20" : "text-orange-300"}
                                        ${isActive ? "ring-4 ring-orange-400/10" : ""}
                                    `}
                                >
                                    {isCompleted ? (
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            transition={{ type: "spring", stiffness: 400, damping: 15 }}
                                        >
                                            <Check size={20} strokeWidth={3} />
                                        </motion.div>
                                    ) : (
                                        <span className="text-sm font-black tracking-tighter">
                                            {index + 1}
                                        </span>
                                    )}
                                </motion.div>

                                {/* Label */}
                                <div className="mt-4 px-1 max-w-[80px] sm:max-w-[120px] text-center">
                                    <p className={`text-[9px] sm:text-[11px] font-black uppercase tracking-widest leading-none sm:leading-tight transition-all duration-300
                                        ${isActive ? "text-orange-500 scale-105" : isCompleted ? "text-gray-600" : "text-gray-300"}`}
                                    >
                                        {step.title}
                                    </p>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
