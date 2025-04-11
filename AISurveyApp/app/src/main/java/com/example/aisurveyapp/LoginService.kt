package com.example.aisurveyapp

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

// Data class to handle response data from Flask
data class LoginResponse(val success: Boolean, val message: String, val session_id: String)
data class LoginRequest(val user_input: String, val password: String)
data class LogoutResponse(val message: String)
data class GoogleTokenRequest(val id_token: String)

interface LoginService {

    // For email/phone login
    @POST("/login")
    fun login(@Body loginRequest: LoginRequest): Call<LoginResponse>

    @POST("/google/token-login")
    fun googleLoginWithToken(@Body tokenRequest: GoogleTokenRequest): Call<LoginResponse>


    // For logout
    @GET("/logout")
    fun logout(): Call<LogoutResponse>

}
