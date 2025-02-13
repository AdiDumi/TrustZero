package com.example.vpnapp;

import android.content.Context
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.example.vpnapp.database.AppDatabase
import com.example.vpnapp.database.PublicKeyItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.FileWriter
import java.io.IOException
import java.security.PublicKey
import java.util.Base64
import kotlin.random.Random


class ExperimentFragment : Fragment(R.layout.experiment_fragment) {

    private val keyViewModel: KeyViewModel by viewModels {
        KeyViewModelFactory(AppDatabase.getDatabase(requireContext()).PublicKeyItemDao())
    }
    private lateinit var usernameEditText: EditText
    private lateinit var passwordEditText: EditText
    private lateinit var ipEditText: EditText
    private lateinit var portEditText: EditText
    private lateinit var numberOfRequest: EditText
    private lateinit var sendRequestButton: Button
    private lateinit var requestNumber: TextView
    private var keys: MutableList<PublicKeyItem> = mutableListOf()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize UI Elements
        usernameEditText = view.findViewById(R.id.usernameEditText)
        passwordEditText = view.findViewById(R.id.passwordEditText)
        ipEditText = view.findViewById(R.id.ipEditText)
        portEditText = view.findViewById(R.id.portEditText)
        numberOfRequest = view.findViewById(R.id.numberOfRequests)
        sendRequestButton = view.findViewById(R.id.sendRequestButton)
        requestNumber = view.findViewById(R.id.requestNumber)

        sendRequestButton.setOnClickListener {
            GlobalScope.launch(Dispatchers.IO) {
                sendRequest()
            }
        }

        // Observe the keys data
        keyViewModel.keys.observe(viewLifecycleOwner) { updatedKeys ->
            keys.clear() // Clear the old data
            keys.addAll(updatedKeys) // Add the new data
        }

        // Load all keys initially (this is where the data fetch happens)
        keyViewModel.getAllKeys()
    }

    private suspend fun sendRequest() {
        val username = usernameEditText.text.toString()
        val password = passwordEditText.text.toString()
        val ip = ipEditText.text.toString()
        val port = portEditText.text.toString()
        val nrOfRequestsString = numberOfRequest.text.toString()

        // Validate inputs
        if (username.isEmpty() || password.isEmpty() || ip.isEmpty() || port.isEmpty() || nrOfRequestsString.isEmpty()) {
            // Show toast on main thread
            withContext(Dispatchers.Main) {
                Toast.makeText(requireContext(), "Please fill all fields", Toast.LENGTH_SHORT)
                    .show()
            }
            return
        }

        val portList = port.split(",")
            .map { it.trim() }
            .filter { it.isNotEmpty() }

        val key = keys.find { it.isInUse }

        if (key == null) {
            // Show toast on main thread
            withContext(Dispatchers.Main) {
                Toast.makeText(
                    requireContext(),
                    "Please select a public key first",
                    Toast.LENGTH_SHORT
                ).show()
            }
            return
        }

        var nrOfRequest = nrOfRequestsString.toInt()
        if (nrOfRequest <= 0)
            nrOfRequest = 1

        // Switch to main thread to update UI
        withContext(Dispatchers.Main) {
            requestNumber.text = "0/$nrOfRequest"
        }

        val client = OkHttpClient()

        val formBody = FormBody.Builder()
            .add("username", username)
            .add("password", password)
            .build()

        var header = publicKeyToPem(key.keyPair.public)

        key.getSignaturesList().forEach { signature -> header = header + ":" + signature.appIdentifier + ":" + signature.signatureText }

        var log = ""

        for (i in 0..nrOfRequest) {
            val randomInt = Random.nextInt(portList.size)
            val url = "http://$ip:${portList[randomInt]}/login"  // Modify endpoint as needed
            val request = Request.Builder()
                .url(url)
                .post(formBody)
                .addHeader("User-Key-Signatures", header)
                .build()
            // Switch to main thread to update UI
            withContext(Dispatchers.Main) {
                requestNumber.text = "$i/$nrOfRequest"
            }
            try {
                val startTime = System.nanoTime()
                // This blocks the current thread and waits for the response
                val response = client.newCall(request).execute()

                val endTime = System.nanoTime()
                if (response.isSuccessful) {
                    // Handle the response (successful request)
                    val durationMs = (endTime - startTime) / 1_000_000 // Convert nanoseconds to milliseconds
                    val durationSeconds = durationMs / 1000.0
                    log = "$log$durationSeconds, "
                    val responseBody = response.body?.string()
                    //println("Response: $responseBody with headers: ${response.headers["User-Key-Signatures"]}")
                    header = response.headers["User-Key-Signatures"].toString()
                } else {
                    // Handle failure response
                    println("Failed Response: ${response.message}")
                    return
                }
            } catch (e: IOException) {
                // Handle error (e.g., network failure)
                println("Error: ${e.localizedMessage}")
            }
        }
        processUserKeySignatures(header, key)
        logToFile(this.requireContext(), log)
    }

    private fun processUserKeySignatures(headerValue: String?, key: PublicKeyItem) {
        if (headerValue.isNullOrEmpty()) return

        val parts = headerValue.split(":")
        if (parts.size < 3) return // Ensure a public key and at least one id-signature pair

        val initialSignatures = key.getSignaturesList()

        // Process id-signature pairs
        for (i in 1 until parts.size step 2) {
            if (i + 1 < parts.size) {
                val id = parts[i]
                val signature = parts[i + 1]
                val index = initialSignatures.indexOfFirst { it.id == id }
                if (index != -1) {
                    initialSignatures[index].signatureText = signature // Update existing signature
                } else {
                    initialSignatures.add(Signature(id, signature, id)) // Adds new signature
                }
            }
        }

        key.updateSignatures(initialSignatures)
        keyViewModel.updatePublicKeyItem(key)
    }

    private fun logToFile(context: Context, data: String) {
        val logFile = File(context.filesDir, "request_logs.txt")
        try {
            FileWriter(logFile, true).use { writer ->
                writer.append(data)
            }
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    private fun publicKeyToPem(publicKey: PublicKey): String {
        val derEncoded = publicKey.encoded // DER-encoded public key
        val base64Encoded = Base64.getEncoder().encodeToString(derEncoded)

        // Wrap with PEM headers
        val pemFormatted = "-----BEGIN PUBLIC KEY-----\n" +
                base64Encoded.chunked(64).joinToString("\n") + // Break into 64-character chunks
                "\n-----END PUBLIC KEY-----"

        return Base64.getEncoder().encodeToString(pemFormatted.toByteArray(Charsets.UTF_8))
    }
}