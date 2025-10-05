
flowchart TD
    A[User Query] --> B[Bot Classifies Intent]
    
    B --> D{Intent Type?}
    
    D -->|text| E[RAG Search<br/>Query ChromaDB for<br/>relevant context]
    D -->|find_image| F[RAG Image Search<br/>Query vector store for<br/>image metadata]
    D -->|generate_chart| G[RAG Data Retrieval<br/>Get relevant data from<br/>ChromaDB]
    D -->|generate_image| H[Find Reference Image<br/>Search database for<br/>user-specified image]
    
    E --> I[Chorus Model Response and Voting]
    
    F --> F1[Filter & Score Results<br/>Apply confidence threshold]
    F1 --> P[Final Response to User]
    
    G --> G1[Parse & Analyze Data<br/>Extract numerical patterns]
    G1 --> G2[Generate Visualization<br/>Create chart with explanation]
    G2 --> P
    
    H --> H1[Find Reference & Process Prompt<br/>Combine user request with image]
    H1 --> H2[AI Image Generation<br/>Create new/edited image]
    H2 --> P
    
    I --> P
    
    P --> Q[Save to Chat History]
    
    %% All boxes with black background and white text
    style A fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style B fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style D fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style E fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style I fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style P fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style Q fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    
    %% Image Search Flow (2 nodes)
    style F fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style F1 fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    
    %% Chart Generation Flow (3 nodes)
    style G fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style G1 fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style G2 fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    
    %% Image Generation Flow (3 nodes)
    style H fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style H1 fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
    style H2 fill:#000000,stroke:#333,stroke-width:2px,color:#ffffff
