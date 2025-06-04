package com.example.myapplication

data class User(
        var name: String,
        // strength
        var armStrength: Int = 0,
        var legStrength: Int = 0,
        var chestStrength: Int = 0,
        // size
        var armSize: Int = 0,
        var legSize: Int = 0,
        var chestSize: Int = 0,
        // about user
        var age: Int = 0,
        var gender: Char = 'M',
        var freqPerWeek: Int = 3,
        var experience: String = "Intermediate",
        // goal stats
        var armGoals: Int = 0,
        var legGoals: Int = 0,
        var chestGoals: Int = 0,
        // workouts done
        var workouts: MutableList<Workout> = mutableListOf()
) {
        fun createGoals(arm: Int, leg: Int, chest: Int) {
                armGoals = arm
                legGoals = leg
                chestGoals = chest
        }

        fun addWorkout(
                exercises: List<Exercise>,
                date: String = ""
        ): Pair<Triple<Int, Int, Int>, Triple<Int, Int, Int>> {
                val workout = Workout(exercises, date)
                workouts.add(workout)
                // Calculate size increases and update User sizes
                val (armSizeInc, chestSizeInc, legSizeInc) = workout.getTotalSizeIncreases()
                armSize += armSizeInc
                legSize += legSizeInc
                chestSize += chestSizeInc
                // Calculate strength increases and update User strengths
                val (armStrengthInc, chestStrengthInc, legStrengthInc) =
                        workout.getTotalStrengthIncreases()
                armStrength += armStrengthInc
                legStrength += legStrengthInc
                chestStrength += chestStrengthInc
                return Pair(
                        Triple(armSizeInc, chestSizeInc, legSizeInc),
                        Triple(armStrengthInc, chestStrengthInc, legStrengthInc)
                )
        }
}

data class Workout(var exercises: List<Exercise>, var date: String = "5/29/2025") {
        fun getTotalSizeIncreases(): Triple<Int, Int, Int> {
                var armIncrease = 0
                var chestIncrease = 0
                var legIncrease = 0

                exercises.forEach { exercise ->
                        when (exercise.targetMuscle) {
                                "Arms" -> armIncrease += exercise.sizeIncrease
                                "Chest" -> chestIncrease += exercise.sizeIncrease
                                "Legs" -> legIncrease += exercise.sizeIncrease
                        }
                }

                return Triple(armIncrease, chestIncrease, legIncrease)
        }

        fun getTotalStrengthIncreases(): Triple<Int, Int, Int> {
                var armStrengthIncrease = 0
                var chestStrengthIncrease = 0
                var legStrengthIncrease = 0

                exercises.forEach { exercise ->
                        when (exercise.targetMuscle) {
                                "Arms" -> armStrengthIncrease += exercise.strengthIncrease
                                "Chest" -> chestStrengthIncrease += exercise.strengthIncrease
                                "Legs" -> legStrengthIncrease += exercise.strengthIncrease
                        }
                }

                return Triple(armStrengthIncrease, chestStrengthIncrease, legStrengthIncrease)
        }
}

data class Exercise(
        var name: String,
        var reps: Int,
        var sets: Int,
        var weights: Int,
        var difficulty: Int,
        var targetMuscle: String
) {
        // these will return unrealistic values - will have model predict values later
        val sizeIncrease: Int
                get() =
                        ((sets * reps * weights * (difficulty / 10.0)).toInt() / 100).coerceAtLeast(
                                1
                        )

        val strengthIncrease: Int
                get() =
                        ((sets * reps * weights * (difficulty / 10.0)).toInt() / 100).coerceAtLeast(
                                1
                        )
}

fun main() {
        val user =
                User(
                        name = "Sagar",
                        age = 25,
                        gender = 'M',
                        freqPerWeek = 3,
                        experience = "Intermediate",
                )

        user.createGoals(200, 200, 200)

        val exercises =
                listOf(
                        Exercise(
                                name = "Bicep Curl",
                                reps = 12,
                                sets = 3,
                                weights = 25,
                                difficulty = 6,
                                targetMuscle = "Arms"
                        ),
                        Exercise(
                                name = "Bench Press",
                                reps = 10,
                                sets = 4,
                                weights = 120,
                                difficulty = 7,
                                targetMuscle = "Chest"
                        ),
                        Exercise(
                                name = "Squat",
                                reps = 8,
                                sets = 5,
                                weights = 200,
                                difficulty = 8,
                                targetMuscle = "Legs"
                        )
                )

        // Add workout and get size and strength increases
        val (sizeIncreases, strengthIncreases) = user.addWorkout(exercises, date = "2025-05-29")
        val (armSizeInc, chestSizeInc, legSizeInc) = sizeIncreases
        val (armStrengthInc, chestStrengthInc, legStrengthInc) = strengthIncreases

        // Print results
        println("Workout added on ${user.workouts[0].date}")
        println(
                "Size Increases - Arms: $armSizeInc mm, Chest: $chestSizeInc mm, Legs: $legSizeInc mm"
        )
        println(
                "Strength Increases - Arms: $armStrengthInc, Chest: $chestStrengthInc, Legs: $legStrengthInc"
        )
        println(
                "Updated User Sizes - Arms: ${user.armSize} mm, Chest: ${user.chestSize} mm, Legs: ${user.legSize} mm"
        )
        println(
                "Updated User Strengths - Arms: ${user.armStrength}, Chest: ${user.chestStrength}, Legs: ${user.legStrength}"
        )
}
