"use client"

import React, { createContext, useContext, ReactNode, useState } from 'react';

// Define the type for your context data
interface AppContextData {
    userName: string;
    setUserName: (name: string) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;

    age: number;
    setAge: (age: number) => void;
    gender: "M" | "F";
    setGender: (gender: "M" | "F") => void;

    // muscle stats (measurements)
    chest: number;
    setChest: (chest: number) => void;
    Back: number;
    setBack: (back: number) => void;
    Traps: number;
    setTraps: (traps: number) => void;
    Biceps: number;
    setBiceps: (biceps: number) => void;

    // muscle tone and body fat

    Experience: "Beginner" | "Intermediate" | "Advanced";
    setExperience: (experience: "Beginner" | "Intermediate" | "Advanced") => void;

    BFP:number;
    setBFP: (bfp: number) => void;

    currentWeight: number;
    setCurrentWeight: (weight: number) => void;
    height: number;
    setHeight: (height: number) => void;

    // genetic advantage between 1-10
    geneticAdvantage: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
    setGeneticAdvantage: (advantage: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10) => void;

    workoutTimeYears: number;
    setWorkoutTimeYears: (years: number) => void;

}

// Create the context with an initial undefined value
const AppContext = createContext<AppContextData | undefined>(undefined);

// Props type for the provider component
interface AppProviderProps {
    children: ReactNode;
}
// Provider component
export function AppProvider({ children }: AppProviderProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [age, setAge] = useState(19);
    const [gender, setGender] = useState<"M" | "F">("M");
    const [chest, setChest] = useState(30);
    const [Back, setBack] = useState(30);
    const [Traps, setTraps] = useState(30);
    const [Biceps, setBiceps] = useState(30);
    const [userName, setUserName] = useState("Sagar");
    const [Experience, setExperience] = useState<"Beginner" | "Intermediate" | "Advanced">("Beginner");
    const [BFP, setBFP] = useState(15);
    const [currentWeight, setCurrentWeight] = useState(60);
    const [height, setHeight] = useState(174);
    const [geneticAdvantage, setGeneticAdvantage] = useState<1|2|3|4|5|6|7|8|9|10>(3);
    const [workoutTimeYears, setWorkoutTimeYears] = useState(1);
    
    const value = {
        isLoading,
        setIsLoading,
        age,
        setAge,
        gender,
        setGender,
        chest,
        setChest,
        Back,
        setBack,
        Traps,
        setTraps,
        Biceps,
        setBiceps,
        userName,
        setUserName,
        Experience,
        setExperience,
        BFP,
        setBFP,
        currentWeight,
        setCurrentWeight,
        height,
        setHeight,
        geneticAdvantage,
        setGeneticAdvantage,
        workoutTimeYears,
        setWorkoutTimeYears,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}


// Custom hook to use the context
export function useAppContext() {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error('useAppContext must be used within an AppProvider');
    }
    return context;
}