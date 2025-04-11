package com.example.aisurveyapp

import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory


object RetrofitClient {

    private const val BASE_URL = "http://10.0.2.2:5000"  // Replace with your Flask server URL
    private var sessionId: String? = null

    fun setSessionId(sessionId: String) {
        this.sessionId = sessionId
    }

    val instance: Retrofit by lazy {
        val okHttpClient = OkHttpClient.Builder().apply {
            addInterceptor { chain ->
                var request = chain.request()
                sessionId?.let {
                    // Add session ID as a custom header
                    request = request.newBuilder()
                        .addHeader("X-Session-ID", it)
                        .build()
                }
                chain.proceed(request)
            }
        }.build()
        val gson = GsonBuilder()
            .setLenient()
            .create()
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }
}
