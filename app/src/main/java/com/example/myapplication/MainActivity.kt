package com.example.myapplication

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.myapplication.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    UserStatsScreen(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(innerPadding)
                    )
                }
            }
        }
    }
}

@Composable
fun UserStatsScreen(modifier: Modifier = Modifier) {
    var userMan by remember { mutableStateOf(User()) } // Reactive User state
    var user by remember { mutableStateOf(User()) } // Reactive User state


    Column(modifier = modifier.padding(16.dp)) {
        Surface(color = Color.Red) {
            Text(
                text = "User Stats",
                modifier = Modifier.padding(16.dp)
            )
        }
        Text(text = "Arm Strength: ${user.armStrength}", modifier = Modifier.padding(top = 8.dp))
        Button(onClick = {
            userMan.trainArms() // Call User function
            user = userMan.copy() // Trigger recomposition
        }) {
            Text("Train Arms")
        }

        Text(text = "Legs Strength: ${user.legStrength}", modifier = Modifier.padding(top = 8.dp))
        Button(onClick = {
            userMan.trainLegs() // Call User function
            user = userMan.copy() // Trigger recomposition
        }) {
            Text("Train Arms")
        }

        Text(text = "Arm Strength: ${user.armStrength}", modifier = Modifier.padding(top = 8.dp))
        Button(onClick = {
            userMan.trainArms() // Call User function
            user = userMan.copy() // Trigger recomposition
        }) {
            Text("Train Arms")
        }



    }
}

@Preview(showBackground = true)
@Composable
fun UserStatsScreenPreview() {
    MyApplicationTheme {
        UserStatsScreen()
    }
}