# Secure Transcriptional AI Assistant for Online Conferences

#### Team: EavesDroppers

#### Team members: Nikita Borisov, Dmitry Dydalyn, Amir Bikineyev

#### Github: [Repository](https://github.com/n-bor1sov/Eavesdropper/tree/dev)

## Description

This web service provides an automated summary of online conferences by processing audio recording. It ensures security by masking sensitive or confidential data during summarization. A de-masking mechanism is employed to allow authorized personnel to access the complete transcription, while safeguarding sensitive information from unauthorized access.

## Method

1. **Audio Segmentation and Clustering:**
   * **Model:** PyAnnote
   * **Description:** PyAnnote Audio is an open-source toolkit for speaker diarization, built on top of PyTorch. It allows for the segmentation and clustering of audio recordings based on speaker characteristics. This step helps in identifying different speakers and their respective speech segments.
2. **Audio Transcription:**
   * **Model:** Whisper (by OpenAI)
   * **Description:** Whisper is a state-of-the-art model for automatic speech recognition (ASR) across multiple languages. It converts audio recordings into text, forming the basis for further processing.
3. **Masking:**
   * The transcript is processed using a Natural Entity Anonymization and Redaction (NEAR) model to mask sensitive and confidential data.
   * This step ensures privacy and data protection.
4. **Summarization:**
   * **Model:** BART (by Facebook AI)
   * **Description:** BART is a powerful model pre-trained for text summarization. It generates a concise summary of the masked transcript, preserving confidentiality.
5. **De-masking:**
   * For authorized users, a de-masking mechanism restores sensitive information, providing access to the full transcription.

## 1. Speech To Text Stage

### PyAnnote Audio

* **Description:** PyAnnote Audio is an open-source toolkit for speaker diarization, built on PyTorch. It offers pre-trained models for speaker identification and diarization.
* **Features:**
  * Pre-trained models for speaker embedding and diarization.
  * Support for overlapped speech detection.
  * Well-suited for diarizing meetings with multiple speakers.
  * Ideal for recognizing speakers in online conferences.

### Whisper (by OpenAI)

**Description:** Whisper is a cutting-edge model designed for automatic speech recognition (ASR) across various languages. Its versatility makes it ideal for transcribing audio recordings into text, forming the foundation for subsequent processing steps.

### Kaldi(optional substitution for PyAnnote)

* **Description:** Kaldi is a flexible speech recognition toolkit with speaker diarization capabilities. It's more complex but offers advanced customization.
* **Features:**
  * Supports various diarization algorithms, including Variational Bayes HMM.
  * Provides tools for clustering speaker embeddings (i-vectors/x-vectors).
  * Suitable for custom speaker diarization tasks.

## 2. NER + Masking Stage

**Encoder Model:**

**Description:** In this stage, we take pretrained encoder model and fine-tune it for Named Entity Recognition (NER) and masking. The model will be fine-tuned on a dataset containing named entities relevant to online conferences.

The NER model identifies and classifies named entities in the transcribed text, allowing us to mask sensitive information effectively.

## 3. Summarization Stage

**Model:** BART (by Facebook AI)

**Description:** BART is a powerful model pre-trained for text summarization. It generates coherent summaries while handling masked transcripts, ensuring confidentiality.

## 4. De-masking Stage

**Method:** Storing unique hash keys for each session

**Description:** We will implement a secure de-masking mechanism using custom hashing functions and methods. This process involves securely storing the original sensitive information and generating unique hash codes for each masked entity and special keys for each session that will make maskig process difficult to unmask unambiguously(for secure reasons).

## Data Insights

### Kaggle Link: [Dataset](https://www.kaggle.com/datasets/rajnathpatel/ner-data?resource=download)

### Overview

We have discovered a valuable dataset containing 48,000 sentences with a diverse range of named entities. This dataset is an excellent resource for training and evaluating Named Entity Recognition (NER) models.

### Dataset Statistics

* **Total Sentences:** 47959
* **Total Words:** 1048565
* **Named Entity Groups:** 8 different special groups

### Named Entity Groups

The dataset covers a wide range of named entity categories, providing a comprehensive collection of real-world entities:

1. geo = Geographical Entity
2. org = Organization
3. per = Person
4. gpe = Geopolitical Entity
5. tim = Time indicator
6. art = Artifact
7. eve = Event
8. nat = Natural Phenomenon

In the scope of our project we will use only part of this groups that is relevant in terms of confidential information in online meetings. Time indications, Artifacts, Natural Phenomenons, will be skiped.
