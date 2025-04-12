package com.example.aisurveyapp

import android.app.DatePickerDialog
import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.util.Calendar
import android.view.View

class MainActivity : AppCompatActivity() {

    private lateinit var etName: EditText
    private lateinit var etBirthDate: EditText
    private lateinit var spinnerEducation: Spinner
    private lateinit var etCity: EditText
    private lateinit var rgGender: RadioGroup
    private lateinit var cbChatGPT: CheckBox
    private lateinit var cbBard: CheckBox
    private lateinit var cbClaude: CheckBox
    private lateinit var cbCopilot: CheckBox
    private lateinit var etUseCase: EditText
    private lateinit var btnSend: Button
    private lateinit var btnLogout: Button
    private lateinit var emailTextView: TextView
    private lateinit var etChatGPTCons: EditText
    private lateinit var etBardCons: EditText
    private lateinit var etClaudeCons: EditText
    private lateinit var etCopilotCons: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        initViews()
        setupListeners()
    }

    private fun initViews() {
        etName = findViewById(R.id.etName)
        etBirthDate = findViewById(R.id.etBirthDate)
        spinnerEducation = findViewById(R.id.spinnerEducation)
        etCity = findViewById(R.id.etCity)
        rgGender = findViewById(R.id.rgGender)
        cbChatGPT = findViewById(R.id.cbChatGPT)
        cbBard = findViewById(R.id.cbBard)
        cbClaude = findViewById(R.id.cbClaude)
        cbCopilot = findViewById(R.id.cbCopilot)
        etChatGPTCons = findViewById(R.id.etChatGPTCons)
        etBardCons = findViewById(R.id.etBardCons)
        etClaudeCons = findViewById(R.id.etClaudeCons)
        etCopilotCons = findViewById(R.id.etCopilotCons)
        etUseCase = findViewById(R.id.etUseCase)
        btnSend = findViewById(R.id.btnSend)
        btnLogout = findViewById(R.id.btnLogout)
        emailTextView = findViewById(R.id.emailTextView)

        val educationLevels = listOf("Select Education Level", "High School", "Bachelor's", "Master's", "PhD")

        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, educationLevels)
        spinnerEducation.adapter = adapter

        spinnerEducation.setSelection(0)

        spinnerEducation.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parentView: AdapterView<*>, view: View?, position: Int, id: Long) {
                checkAllFields()
            }

            override fun onNothingSelected(parentView: AdapterView<*>) {
                checkAllFields()
            }
        }


        val emailFromIntent = intent.getStringExtra("user_email")
        if (!emailFromIntent.isNullOrEmpty()) {
            emailTextView.text = "Email: $emailFromIntent"
        } else {
            val account: GoogleSignInAccount? = GoogleSignIn.getLastSignedInAccount(this)
            emailTextView.text = "Email: ${account?.email}"
        }
    }

    private fun setupListeners() {
        val textWatcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) = checkAllFields()
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        }

        etName.addTextChangedListener(textWatcher)
        etBirthDate.addTextChangedListener(textWatcher)
        etCity.addTextChangedListener(textWatcher)
        cbChatGPT.setOnCheckedChangeListener { _, isChecked ->
            etChatGPTCons.visibility = if (isChecked) View.VISIBLE else View.GONE
        }

        cbBard.setOnCheckedChangeListener { _, isChecked ->
            etBardCons.visibility = if (isChecked) View.VISIBLE else View.GONE
        }

        cbClaude.setOnCheckedChangeListener { _, isChecked ->
            etClaudeCons.visibility = if (isChecked) View.VISIBLE else View.GONE
        }

        cbCopilot.setOnCheckedChangeListener { _, isChecked ->
            etCopilotCons.visibility = if (isChecked) View.VISIBLE else View.GONE
        }
        etUseCase.addTextChangedListener(textWatcher)
        rgGender.setOnCheckedChangeListener { _, _ -> checkAllFields() }

        etBirthDate.setOnClickListener {
            val c = Calendar.getInstance()
            val today = Calendar.getInstance()

            DatePickerDialog(
                this,
                { _, y, m, d ->
                    val selectedDate = Calendar.getInstance().apply {
                        set(y, m, d)
                        set(Calendar.HOUR_OF_DAY, 0)
                        set(Calendar.MINUTE, 0)
                        set(Calendar.SECOND, 0)
                        set(Calendar.MILLISECOND, 0)
                    }

                    val errorMessage: TextView = findViewById(R.id.birthdateErrorMessage)

                    if (selectedDate.after(today)) {
                        errorMessage.visibility = View.VISIBLE
                        etBirthDate.text.clear()
                        checkAllFields()
                    } else {
                        errorMessage.visibility = View.GONE
                        etBirthDate.setText(String.format("%04d-%02d-%02d", y, m + 1, d))
                        checkAllFields()
                    }
                },
                c.get(Calendar.YEAR),
                c.get(Calendar.MONTH),
                c.get(Calendar.DAY_OF_MONTH)
            ).show()
        }


        btnSend.setOnClickListener { sendSurveyData() }
        btnLogout.setOnClickListener { logoutUser() }
    }

    private fun checkAllFields() {
        val allFilled = etName.text.isNotBlank() &&
                spinnerEducation.selectedItemPosition != 0 &&
                etBirthDate.text.isNotBlank() &&
                etCity.text.isNotBlank() &&
                etUseCase.text.isNotBlank() &&
                rgGender.checkedRadioButtonId != -1
        btnSend.isEnabled = allFilled
    }

    private fun sendSurveyData() {
        val selectedModels = mutableListOf<String>()
        val modelConsMap = mutableMapOf<String, String>()
        val errorMessage: TextView = findViewById(R.id.aiModelErrorMessage)
        if (cbChatGPT.isChecked) {
            selectedModels.add(cbChatGPT.text.toString())
            modelConsMap["ChatGPT"] = etChatGPTCons.text.toString()
        }
        if (cbBard.isChecked) {
            selectedModels.add(cbBard.text.toString())
            modelConsMap["Bard"] = etBardCons.text.toString()
        }
        if (cbClaude.isChecked) {
            selectedModels.add(cbClaude.text.toString())
            modelConsMap["Claude"] = etClaudeCons.text.toString()
        }
        if (cbCopilot.isChecked) {
            selectedModels.add(cbCopilot.text.toString())
            modelConsMap["Copilot"] = etCopilotCons.text.toString()
        }
        if (selectedModels.isEmpty()) {
            errorMessage.visibility = View.VISIBLE
            btnSend.isEnabled = false
            return
        } else {
            errorMessage.visibility = View.GONE
            btnSend.isEnabled = true
        }
        val request = SurveyRequest(
            name = etName.text.toString(),
            birth_date = etBirthDate.text.toString(),
            education_level = spinnerEducation.selectedItem.toString(),
            city = etCity.text.toString(),
            gender = findViewById<RadioButton>(rgGender.checkedRadioButtonId).text.toString(),
            models_tried = selectedModels,
            model_cons = modelConsMap,
            use_case = etUseCase.text.toString()
        )

        val api = RetrofitClient.instance.create(MainActivityService::class.java)
        api.sendSurvey(request).enqueue(object : Callback<SurveyResponse> {
            override fun onResponse(call: Call<SurveyResponse>, response: Response<SurveyResponse>) {
                if (response.isSuccessful && response.body()?.success == true) {
                    Toast.makeText(this@MainActivity, "Survey mailed ✔", Toast.LENGTH_SHORT).show()
                    finish()
                } else {
                    Toast.makeText(this@MainActivity, "Send failed", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<SurveyResponse>, t: Throwable) {
                Toast.makeText(this@MainActivity, "Network error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }


    private fun logoutUser() {
        val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestEmail()
            .build()
        val googleSignInClient = GoogleSignIn.getClient(this, gso)
        googleSignInClient.revokeAccess().addOnCompleteListener {
            val apiService = RetrofitClient.instance.create(LoginService::class.java)
            apiService.logout().enqueue(object : Callback<LogoutResponse> {
                override fun onResponse(call: Call<LogoutResponse>, response: Response<LogoutResponse>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@MainActivity, "Logged out successfully", Toast.LENGTH_SHORT).show()
                        startActivity(Intent(this@MainActivity, LoginActivity::class.java))
                        finish()
                    } else {
                        Toast.makeText(this@MainActivity, "Logout failed", Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onFailure(call: Call<LogoutResponse>, t: Throwable) {
                    Toast.makeText(this@MainActivity, "Network error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }
    }
}
