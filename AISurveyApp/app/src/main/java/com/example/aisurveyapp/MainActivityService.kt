package com.example.aisurveyapp

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

data class SurveyRequest(
    val name: String,
    val birth_date: String,
    val education_level: String,
    val city: String,
    val gender: String,
    val models_tried: List<String>,
    val model_cons: Map<String, String>,
    val use_case: String
)


data class SurveyResponse(
    val success: Boolean,
    val message: String
)

interface MainActivityService {
    @POST("/survey/send")
    fun sendSurvey(@Body body: SurveyRequest): Call<SurveyResponse>
}
