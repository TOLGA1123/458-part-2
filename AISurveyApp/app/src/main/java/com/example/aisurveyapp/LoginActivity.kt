package com.example.aisurveyapp

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.media3.common.util.Log
import androidx.media3.common.util.UnstableApi
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.ApiException
import org.json.JSONObject
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

@UnstableApi
class LoginActivity : AppCompatActivity() {

    private lateinit var etUserInput: EditText
    private lateinit var etPassword: EditText
    private lateinit var btnLogin: Button
    private lateinit var btnGoogleLogin: Button
    private lateinit var googleSignInClient: GoogleSignInClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        etUserInput = findViewById(R.id.etUserInput)
        etPassword = findViewById(R.id.etPassword)
        btnLogin = findViewById(R.id.btnLogin)
        btnGoogleLogin = findViewById(R.id.btnGoogleLogin)

        // Standard login
        btnLogin.setOnClickListener {
            val userInput = etUserInput.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (userInput.isNotEmpty() && password.isNotEmpty()) {
                loginUser(userInput, password)
            } else {
                Toast.makeText(this, "Please enter email/phone and password", Toast.LENGTH_SHORT).show()
            }
        }

        // Configure Google Sign-In
        val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken("1045716424808-g5ckn3rgeuj0h628f2acbershk2p5vc9.apps.googleusercontent.com") // web client id stack overflow
            .requestEmail()
            .build()

        googleSignInClient = GoogleSignIn.getClient(this, gso)

        // Google login button click
        btnGoogleLogin.setOnClickListener {
            googleSignInClient.signOut().addOnCompleteListener {
                googleSignInClient.revokeAccess() // This ensures that the session is completely reset
                    .addOnCompleteListener {
                        googleLogin() // Trigger Google login after revoking access
                    }
        }
    }
    }

    private fun loginUser(userInput: String, password: String) {
        val loginRequest = LoginRequest(userInput, password)
        val apiService = RetrofitClient.instance.create(LoginService::class.java)

        apiService.login(loginRequest).enqueue(object : Callback<LoginResponse> {
            override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                if (response.isSuccessful && response.body()?.session_id != null) {
                    val sessionId = response.body()?.session_id
                    startMainActivity(sessionId)
                    val emailEditText = findViewById<EditText>(R.id.etUserInput)
                    val enteredEmail = emailEditText.text.toString()
                    val intent = Intent(this@LoginActivity, MainActivity::class.java)
                    intent.putExtra("user_email", enteredEmail)  // enteredEmail is the logged-in email
                    startActivity(intent)
                    finish()
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = try {
                        val json = JSONObject(errorBody.toString())
                        json.getString("error")
                    } catch (e: Exception) {
                        "Login failed. Please try again."
                    }
                    Toast.makeText(this@LoginActivity, errorMessage, Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                Toast.makeText(this@LoginActivity, "Network error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun googleLogin() {
        val signInIntent = googleSignInClient.signInIntent
        signInLauncher.launch(signInIntent)
    }


    private val signInLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                val data = result.data
                val task = GoogleSignIn.getSignedInAccountFromIntent(data)
                try {
                    val account = task.getResult(ApiException::class.java)
                    val idToken = account?.idToken
                    if (idToken != null) {
                        sendIdTokenToServer(idToken)
                    } else {
                        Toast.makeText(this, "Google ID Token is null", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: ApiException) {
                    Log.e("GoogleSignIn", "ApiException: ${e.statusCode} - ${e.message}")
                    Toast.makeText(this, "Google sign in failed: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(this, "Google sign-in failed", Toast.LENGTH_SHORT).show()
            }
        }


    private fun sendIdTokenToServer(idToken: String) {
        val apiService = RetrofitClient.instance.create(LoginService::class.java)
        val tokenRequest = GoogleTokenRequest(id_token = idToken)

        apiService.googleLoginWithToken(tokenRequest).enqueue(object : Callback<LoginResponse> {
            override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                if (response.isSuccessful && response.body()?.session_id != null) {
                    val sessionId = response.body()?.session_id
                    startMainActivity(sessionId)
                } else {
                    Toast.makeText(this@LoginActivity, "Google login failed", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                Toast.makeText(this@LoginActivity, "Network error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun startMainActivity(sessionId: String?) {
        val intent = Intent(this, MainActivity::class.java)
        intent.putExtra("session_id", sessionId)
        startActivity(intent)
        finish()
    }
}
