package com.capture.app.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.AttachFile
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.FolderOpen
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.AssistChip
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.InputChip
import androidx.compose.material3.InputChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.capture.app.data.CaptureRepository
import com.capture.app.data.PreferencesManager
import com.capture.app.model.Attachment
import com.capture.app.model.CaptureData
import com.capture.app.model.CaptureSource
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun CaptureScreen(
    initialText: String = "",
    initialAttachments: List<Attachment> = emptyList(),
    source: CaptureSource = CaptureSource.Direct,
    onSaved: () -> Unit = {},
    onFolderPick: () -> Unit = {}
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val prefs = remember { PreferencesManager(context) }
    val repo = remember { CaptureRepository(context) }
    val snackbarHostState = remember { SnackbarHostState() }

    var text by remember { mutableStateOf(initialText) }
    val attachments = remember { mutableStateListOf<Attachment>().apply { addAll(initialAttachments) } }
    val tags = remember { mutableStateListOf<String>() }
    var tagInput by remember { mutableStateOf("") }
    var isSaving by remember { mutableStateOf(false) }

    val saveLocationDisplay by prefs.saveLocationDisplay.collectAsState(initial = "Not set — tap to choose")
    val allTags by prefs.allTags.collectAsState(initial = emptySet())

    val focusRequester = remember { FocusRequester() }

    // Image picker
    val imagePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetMultipleContents()
    ) { uris ->
        uris.forEach { uri ->
            val mimeType = context.contentResolver.getType(uri)
            attachments.add(Attachment(uri = uri, mimeType = mimeType, displayName = null))
        }
    }

    // File picker
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri ->
        uri?.let {
            val mimeType = context.contentResolver.getType(it)
            attachments.add(Attachment(uri = it, mimeType = mimeType, displayName = null))
        }
    }

    // Auto-focus text field
    LaunchedEffect(Unit) {
        focusRequester.requestFocus()
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Capture",
                        style = MaterialTheme.typography.titleMedium
                    )
                },
                actions = {
                    // Save button — always visible
                    FilledTonalButton(
                        onClick = {
                            if (isSaving) return@FilledTonalButton
                            isSaving = true
                            scope.launch {
                                val data = CaptureData(
                                    text = text,
                                    tags = tags.toList(),
                                    attachments = attachments.toList(),
                                    source = source
                                )
                                val result = repo.save(data)
                                result.fold(
                                    onSuccess = { msg ->
                                        snackbarHostState.showSnackbar(msg)
                                        onSaved()
                                    },
                                    onFailure = { err ->
                                        snackbarHostState.showSnackbar(err.message ?: "Save failed")
                                        isSaving = false
                                    }
                                )
                            }
                        },
                        enabled = !isSaving && (text.isNotBlank() || attachments.isNotEmpty()),
                        modifier = Modifier.padding(end = 8.dp)
                    ) {
                        Icon(
                            Icons.Default.Check,
                            contentDescription = "Save",
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(Modifier.width(4.dp))
                        Text("Save")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .imePadding()
                .verticalScroll(rememberScrollState())
        ) {
            // Main text field
            OutlinedTextField(
                value = text,
                onValueChange = { text = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 200.dp)
                    .padding(horizontal = 16.dp)
                    .focusRequester(focusRequester),
                placeholder = { Text("Start typing…") },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                    unfocusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.15f),
                ),
                shape = MaterialTheme.shapes.medium
            )

            Spacer(Modifier.height(8.dp))

            // Attach buttons row
            Row(
                modifier = Modifier.padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                AssistChip(
                    onClick = { imagePickerLauncher.launch("image/*") },
                    label = { Text("Image") },
                    leadingIcon = {
                        Icon(Icons.Default.Image, contentDescription = null, modifier = Modifier.size(18.dp))
                    }
                )
                AssistChip(
                    onClick = { filePickerLauncher.launch(arrayOf("*/*")) },
                    label = { Text("File") },
                    leadingIcon = {
                        Icon(Icons.Default.AttachFile, contentDescription = null, modifier = Modifier.size(18.dp))
                    }
                )
            }

            // Attachment previews
            AnimatedVisibility(
                visible = attachments.isNotEmpty(),
                enter = fadeIn(),
                exit = fadeOut()
            ) {
                LazyRow(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(attachments, key = { it.uri.toString() }) { attachment ->
                        AttachmentPreview(
                            attachment = attachment,
                            onRemove = { attachments.remove(attachment) }
                        )
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            // Tags section
            Column(modifier = Modifier.padding(horizontal = 16.dp)) {
                Text(
                    "Tags",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(Modifier.height(4.dp))

                // Current tags as chips
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    tags.forEach { tag ->
                        InputChip(
                            selected = false,
                            onClick = { tags.remove(tag) },
                            label = { Text(tag) },
                            trailingIcon = {
                                Icon(
                                    Icons.Default.Close,
                                    contentDescription = "Remove $tag",
                                    modifier = Modifier.size(InputChipDefaults.IconSize)
                                )
                            }
                        )
                    }
                }

                // Tag input
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    OutlinedTextField(
                        value = tagInput,
                        onValueChange = { tagInput = it },
                        modifier = Modifier.weight(1f),
                        placeholder = { Text("Add tag…") },
                        singleLine = true,
                        textStyle = MaterialTheme.typography.bodySmall,
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                        keyboardActions = KeyboardActions(
                            onDone = {
                                val trimmed = tagInput.trim().lowercase()
                                if (trimmed.isNotEmpty() && trimmed !in tags) {
                                    tags.add(trimmed)
                                }
                                tagInput = ""
                            }
                        ),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                            unfocusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.15f),
                        ),
                        shape = MaterialTheme.shapes.small
                    )

                    IconButton(
                        onClick = {
                            val trimmed = tagInput.trim().lowercase()
                            if (trimmed.isNotEmpty() && trimmed !in tags) {
                                tags.add(trimmed)
                            }
                            tagInput = ""
                        }
                    ) {
                        Icon(Icons.Default.Add, contentDescription = "Add tag")
                    }
                }

                // Suggested tags from history
                AnimatedVisibility(visible = allTags.isNotEmpty()) {
                    FlowRow(
                        modifier = Modifier.padding(top = 4.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        allTags
                            .filter { it !in tags }
                            .take(10)
                            .forEach { suggestion ->
                                AssistChip(
                                    onClick = {
                                        if (suggestion !in tags) tags.add(suggestion)
                                    },
                                    label = {
                                        Text(
                                            suggestion,
                                            style = MaterialTheme.typography.labelSmall
                                        )
                                    }
                                )
                            }
                    }
                }
            }

            Spacer(Modifier.height(24.dp))

            // Save location — lowkey, at the bottom
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onFolderPick() }
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.FolderOpen,
                    contentDescription = "Save location",
                    modifier = Modifier.size(16.dp),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = saveLocationDisplay,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }
    }
}

@Composable
private fun AttachmentPreview(
    attachment: Attachment,
    onRemove: () -> Unit
) {
    Box(
        modifier = Modifier
            .size(80.dp)
            .clip(MaterialTheme.shapes.small)
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                if (attachment.mimeType?.startsWith("image/") == true)
                    Icons.Default.Image
                else
                    Icons.Default.AttachFile,
                contentDescription = "Attached file",
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = attachment.displayName ?: attachment.mimeType?.substringAfter("/") ?: "file",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f),
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(2.dp),
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }

        // Remove button
        IconButton(
            onClick = onRemove,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .size(24.dp)
        ) {
            Icon(
                Icons.Default.Close,
                contentDescription = "Remove",
                modifier = Modifier.size(14.dp),
                tint = MaterialTheme.colorScheme.error
            )
        }
    }
}
