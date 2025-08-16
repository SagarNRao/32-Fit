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
    BFP:number;

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
    const [age, setAge] = useState(0);
    const [gender, setGender] = useState<"M" | "F">("M");
    const [chest, setChest] = useState(0);
    const [Back, setBack] = useState(0);
    const [Traps, setTraps] = useState(0);
    const [Biceps, setBiceps] = useState(0);
    const [userName, setUserName] = useState("");

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
        setUserName
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