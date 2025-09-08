import { useAppContext } from "@/app/appContext";
import React from "react";
import { useState, useContext, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Image from "next/image";

interface UserAvatarProps {
  armsSizePred: number;
  chestSizePred: number;
  quadsSizePred: number;
  TrapsSizePred: number;
}

export default function UserAvatar(props: UserAvatarProps) {
  const [mode, setMode] = useState<"Bulk" | "Cut" | "Fat" | "">("");

  const {
    userName,
    setUserName,
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
  } = useAppContext();

  // get definition
  const getDefinition = () => {
    // USING CURRENT WEIGHT AS PREDICTED WEIGHT FOR NOW CHANGE THIS LATER
    // TODO: Update to use predicted_weight from model when available

    const predicted_weight = currentWeight;

    const training_intensity = workoutTimeYears * 100;
    const muscle_gain_factor = 1 + training_intensity * 0.001;

    const muscle_mass = predicted_weight * (1 - BFP / 100) * muscle_gain_factor;

    const definition_raw = ((muscle_mass / 10) * (50 - BFP)) / 10;

    // Scale to 0-5 range (updated from 0-10)
    const definition_score = Math.max(0, Math.min(5, definition_raw / 2));

    // converting size to 1-5 range for sprite selection (props are now 0-5)
    const armsSizeScaled = Math.ceil(
      Math.max(1, Math.min(5, props.armsSizePred))
    );
    const chestSizeScaled = Math.ceil(
      Math.max(1, Math.min(5, props.chestSizePred))
    );
    const quadsSizeScaled = Math.ceil(
      Math.max(1, Math.min(5, props.quadsSizePred))
    );
    const trapsSizeScaled = Math.ceil(
      Math.max(1, Math.min(5, props.TrapsSizePred))
    );

    return {
      muscle_mass: Math.round(muscle_mass * 10) / 10,
      definition_score: Math.round(definition_score * 10) / 10,
      training_intensity: training_intensity,
      sizes: {
        arms: armsSizeScaled,
        chest: chestSizeScaled,
        quads: quadsSizeScaled,
        traps: trapsSizeScaled,
      },
    };
  };


  const stats = getDefinition();

  // Use useEffect to set mode based on definition score to avoid infinite re-renders
  useEffect(() => {
    if (stats.definition_score < 2.5) {
      setMode("Cut");
    } else {
      setMode("Bulk");
    }
  }, [stats.definition_score]);

  const squareDims = 150;

  // Ensure mode has a fallback value
  const currentMode = mode || "Cut";

  return (
    <div className="flex flex-row">
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-xl">
        {userName}&apos;s Avatar Stats
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Main Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
          <p className="text-2xl font-bold text-green-600">
            {stats.muscle_mass} kg
          </p>
          <p className="text-sm text-muted-foreground">Muscle Mass</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
          <p className="text-2xl font-bold text-blue-600">
            {stats.definition_score}/5
          </p>
          <p className="text-sm text-muted-foreground">
            Definition Score
          </p>
            </div>
          </CardContent>
        </Card>
          </div>

          {/* Base Statistics */}
          <Card>
        <CardHeader>
          <CardTitle className="text-sm">Base Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex justify-between">
          <span className="text-muted-foreground">Weight:</span>
          <span className="font-medium">{currentWeight} kg</span>
            </div>
            <div className="flex justify-between">
          <span className="text-muted-foreground">Body Fat:</span>
          <span className="font-medium">{BFP}%</span>
            </div>
            <div className="flex justify-between">
          <span className="text-muted-foreground">Training Years:</span>
          <span className="font-medium">{workoutTimeYears}</span>
            </div>
            <div className="flex justify-between">
          <span className="text-muted-foreground">
            Training Intensity:
          </span>
          <span className="font-medium">
            {stats.training_intensity}
          </span>
            </div>
          </div>
        </CardContent>
          </Card>

          {/* Muscle Development */}
          <Card>
        <CardHeader>
          <CardTitle className="text-sm">
            Muscle Development (0-10)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            <Card className="p-3">
          <div className="text-center">
            <p className="text-lg font-bold text-purple-600">
              {stats.sizes.arms}
            </p>
            <p className="text-xs text-muted-foreground">Arms</p>
          </div>
            </Card>
            <Card className="p-3">
          <div className="text-center">
            <p className="text-lg font-bold text-purple-600">
              {stats.sizes.chest}
            </p>
            <p className="text-xs text-muted-foreground">Chest</p>
          </div>
            </Card>
            <Card className="p-3">
          <div className="text-center">
            <p className="text-lg font-bold text-purple-600">
              {stats.sizes.quads}
            </p>
            <p className="text-xs text-muted-foreground">Quads</p>
          </div>
            </Card>
            <Card className="p-3">
          <div className="text-center">
            <p className="text-lg font-bold text-purple-600">
              {stats.sizes.traps}
            </p>
            <p className="text-xs text-muted-foreground">Traps</p>
          </div>
            </Card>
          </div>
        </CardContent>
          </Card>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          {/* CHEST */}
          <Image className="border"
            src={`/sprites/${currentMode}_Chest_${stats.sizes.chest}.png`}
            alt="Chest muscle"
            width={squareDims}
            height={squareDims}
          />
          {/* ARMS */}
          <Image className="border"
            src={`/sprites/${currentMode}_Arms_${stats.sizes.arms}.png`}
            alt="Arms muscle"
            width={squareDims}
            height={squareDims}
          />
          {/* BACK/TRAPS */}
          <Image className="border"
            src={`/sprites/${currentMode}_Back_${stats.sizes.traps}.png`}
            alt="Back muscle"
            width={squareDims}
            height={squareDims}
          />
          {/* QUADS */}
          <Image className="border"
            src={`/sprites/${currentMode}_Quads_${stats.sizes.quads}.png`}
            alt="Quads muscle"
            width={squareDims}
            height={squareDims}
          />
        </CardContent>
      </Card>
    </div>
  );
}
