"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import axios from "axios";

interface User {
  name: string;
  age: number;
  gender: "M" | "F";
  backSize: number;
  chestSize: number;
  quadsSize: number;
  frequency: number;
  protein: number;
  calories: number;
  sleep: number;
  experience: "Beginner" | "Intermediate" | "Advanced";
}

interface Exercise {
  name: string;
  targetMuscle: string;
  sets: number;
  reps: number;
  weight: number;
  difficulty: number;
}

interface Prediction {
  [muscle: string]: number;
}

export default function WorkoutForm() {
  const [workout, setWorkout] = useState<Exercise[] | null>(null);
  const [proteinIntake, setProteinIntake] = useState<number>();
  const [predictions, setPredictions] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);

  const userHere: User = {
    name: "John Doe",
    age: 25,
    gender: "M",
    backSize: 80,
    chestSize: 95,
    quadsSize: 60,
    frequency: 3,
    protein: 140, // Updated to a reasonable value
    calories: 2800,
    sleep: 8,
    experience: "Beginner",
  };

  const handleAddExercise = (e: React.MouseEvent<HTMLButtonElement>) => {
    const form = e.currentTarget
      .closest("div")
      ?.querySelectorAll("input, select");
    if (!form) return;

    const formData = new FormData();
    form.forEach((element) => {
      if (
        element instanceof HTMLInputElement ||
        element instanceof HTMLSelectElement
      ) {
        formData.append(element.name, element.value);
      }
    });

    const exercise: Exercise = {
      name: formData.get("name") as string,
      targetMuscle: formData.get("targetMuscle") as string,
      sets: Number(formData.get("sets")),
      reps: Number(formData.get("reps")),
      weight: Number(formData.get("weight")),
      difficulty: Number(formData.get("difficulty")),
    };

    setWorkout((prev) => (prev ? [...prev, exercise] : [exercise]));
    form.forEach((element) => {
      if (
        element instanceof HTMLInputElement ||
        element instanceof HTMLSelectElement
      ) {
        element.value = "";
      }
    });

    console.log("WORKOUT HERE", workout);
  };

  const getSizeProgress = async () => {
    if (!workout || workout.length === 0) {
      setError("No exercises added to predict.");
      return;
    }

    // Map workout to the format expected by the server
    const exercises = workout.map((ex) => ({
      exercise_type: ex.name,
      sets: ex.sets,
      reps: ex.reps,
      weight: ex.weight,
      target_muscle_group: "Quads", 
      exercise_category: "Compound"
    }));

    const payload = {
      age: userHere.age,
      gender: userHere.gender,
      exercises,
      frequency: userHere.frequency,
      protein: userHere.protein,
      calories: userHere.calories,
      sleep: userHere.sleep,
      experience: userHere.experience,
    };

    console.log("PAYLOAD HERE", payload)

    try {
      const response = await axios.post(
        "http://localhost:5000/predict",
        payload
      );
      setPredictions(response.data.predictions);
      console.log(predictions);
      setError(null);
      console.log("Progress response:", response.data);
    } catch (error) {
      console.error("Error getting progress:", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Add Exercise</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            name="name"
            placeholder="Exercise name (e.g., Squats)"
            required
          />
          <Select name="targetMuscle" required>
            <SelectTrigger>
              <SelectValue placeholder="Select muscle group" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Back">Back</SelectItem>
              <SelectItem value="Chest">Chest</SelectItem>
              <SelectItem value="Quads">Quads</SelectItem>
            </SelectContent>
          </Select>
          <Input
            name="sets"
            type="number"
            placeholder="Number of sets (1-10)"
            required
            min="1"
            max="10"
          />
          <Input
            name="reps"
            type="number"
            placeholder="Number of reps (1-20)"
            required
            min="1"
            max="20"
          />
          <Input
            name="weight"
            type="number"
            placeholder="Weight (kg, 0-300)"
            required
            min="0"
            max="300"
          />
          <Input
            name="difficulty"
            type="number"
            min="1"
            max="10"
            placeholder="Difficulty (1-10, ≥5 for Compound)"
            required
          />
          <Button className="w-full" onClick={handleAddExercise}>
            Add Exercise
          </Button>
        </CardContent>
      </Card>

      <Button onClick={() => getSizeProgress()}>Get size progress</Button>

      {workout && workout.length > 0 && (
        <Card className="mt-8 w-full max-w-md">
          <CardHeader>
            <CardTitle>Current Workout</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {workout.map((exercise, index) => (
                <li key={index} className="p-2 border rounded">
                  {exercise.name} - {exercise.targetMuscle} - {exercise.sets}x
                  {exercise.reps} @ {exercise.weight}kg (Difficulty:{" "}
                  {exercise.difficulty})
                </li>
              ))}
            </ul>
            <Button className="w-full mt-4" onClick={getSizeProgress}>
              Get Muscle Growth Prediction
            </Button>
          </CardContent>
        </Card>
      )}

      {predictions && (
        <Card className="mt-8 w-full max-w-md">
          <CardHeader>
            <CardTitle>Predicted Muscle Growth (12 Weeks)</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {Object.entries(predictions).map(([muscle, growth]) => (
                <li key={muscle} className="p-2 border rounded">
                  {muscle}: {growth.toFixed(2)} cm²
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="mt-8 w-full max-w-md">
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-500">{error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
