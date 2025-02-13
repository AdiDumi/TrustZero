package com.example.vpnapp

import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.net.VpnService
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.Button
import android.widget.Spinner
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity.RESULT_OK
import androidx.appcompat.content.res.AppCompatResources
import androidx.fragment.app.Fragment

class HomeFragment : Fragment(R.layout.home_fragment) {
    private lateinit var appSpinner: Spinner
    private lateinit var appList: List<AppInfo>
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    // Variable to store the selected app's package
    private var selectedAppPackage: String? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        appSpinner = view.findViewById(R.id.app_spinner)
        startButton = view.findViewById(R.id.start_button)
        stopButton = view.findViewById(R.id.stop_button)

        appList = getInstalledApps()

        // Create an adapter for the spinner
        val adapter = AppSpinnerAdapter(requireContext(), appList)
        appSpinner.adapter = adapter

        // Handle selection from the dropdown
        appSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                if (position != 0) { // Skip placeholder at index 0
                    val selectedApp = appList[position]
                    // Perform desired action with the selected app
                    selectedAppPackage = selectedApp.packageName // Save the selected package
                    startButton.isEnabled = true // Enable the start button
                }
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {
                selectedAppPackage = null
                startButton.isEnabled = false // Disable the start button
                stopButton.isEnabled = false // Disable the stop button
            }
        }

        // Set up the Start button click listener
        startButton.setOnClickListener {
            if (selectedAppPackage != null) {
//                val intent = Intent(this, MyVpnService::class.java)
//                intent.putExtra("selectedAppPackage", selectedAppPackage)
//                startService(intent) // Start the VPN service with the selected app
                startVpnService()
                stopButton.isEnabled = true // Enable the Stop button once VPN is started
                startButton.isEnabled = false // Disable the Start button
            } else {
                Toast.makeText(requireContext(), "Please select an app first", Toast.LENGTH_SHORT).show()
            }
        }

        // Set up the Stop button's onClickListener
        stopButton.setOnClickListener {
            //stopService(Intent(this, MyVpnService::class.java)) // Stop the VPN service
            stopVpnService()
            stopButton.isEnabled = false // Disable the Stop button after stopping the service
        }
    }

    private fun startVpnService() {
        val vpnIntent = VpnService.prepare(requireContext())
        if (vpnIntent != null) {
            startActivityForResult(vpnIntent, 0)
        } else {
            onActivityResult(0, RESULT_OK, null)
        }
    }

    private fun stopVpnService() {
        val intent = Intent(requireContext(), MyVpnService::class.java)
        requireContext().stopService(intent)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 0 && resultCode == RESULT_OK) {
            val intent = Intent(requireContext(), MyVpnService::class.java)
            intent.putExtra("selectedAppPackage", selectedAppPackage)
            requireContext().startService(intent)
        }
    }

    private fun getInstalledApps(): List<AppInfo> {
        val placeholder = AppInfo("Select an app", AppCompatResources.getDrawable(requireContext(), R.drawable.ic_android_black_24dp)!!, "")
        val packageManager = requireContext().packageManager
        val installedApps = packageManager.getInstalledApplications(PackageManager.GET_META_DATA)

        val appList = installedApps.filter { app ->
            (app.flags and ApplicationInfo.FLAG_SYSTEM) == 0
        }.map { app ->
            AppInfo(
                name = packageManager.getApplicationLabel(app).toString(),
                icon = packageManager.getApplicationIcon(app),
                packageName = app.packageName
            )
        }
        return listOf(placeholder) + appList // Add the placeholder to the top of the list
    }
}