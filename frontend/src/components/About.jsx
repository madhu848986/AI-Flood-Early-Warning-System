
import React from "react";

function About() {
  const sections = [
    {
      title: "Project Overview",
      content:
        "The AI-Driven Multimodal Flood Early-Warning and Dynamic Safe-Zone Recommendation System is designed to estimate flood risk and support safer decision-making in the Koshi Basin, Nepal.",
    },
    {
      title: "Project Objectives",
      content: [
        "Estimate flood risk using rainfall, elevation and flood observation data.",
        "Provide flood-risk information through an interactive map.",
        "Recommend potentially safer locations based on estimated risk.",
        "Identify potential shelters and compare possible routes.",
        "Support early awareness and emergency preparedness.",
      ],
    },
    {
      title: "Technologies Used",
      content: [
        "Frontend: React.js",
        "Backend: Python and FastAPI",
        "Machine Learning: Random Forest and XGBoost",
        "Database and Data Processing: Python, Pandas",
        "Mapping: OpenStreetMap and Geographic data",
      ],
    },
    {
      title: "Data Sources",
      content: [
        "GPM IMERG – Rainfall data",
        "MODIS – Flood observation data",
        "SRTM – Elevation data",
        "OpenStreetMap – Roads and potential shelter locations",
      ],
    },
  ];

  const emergencyGuidelines = [
    "Move to higher ground when flooding is expected or occurring.",
    "Stay away from rivers, streams and drainage channels during floods.",
    "Never walk, swim or drive through floodwater.",
    "Follow instructions and warnings issued by local authorities.",
    "Keep drinking water, medicines, food, a torch and essential documents ready.",
    "Avoid damaged electrical equipment and fallen power lines.",
    "Use only officially confirmed evacuation shelters and routes.",
  ];

  const usageSteps = [
    "Dashboard – View the overall project information.",
    "Flood Risk Map – Explore estimated flood-risk areas.",
    "Flood Forecast & Alerts – View available rainfall and flood-risk forecasts.",
    "Safest Place – Explore potentially lower-risk locations.",
    "Safest Route – Compare possible routes to a destination.",
    "Shelter Finder – Explore potential shelter locations.",
  ];

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.heading}>About & Emergency Information</h1>
        <p style={styles.subtitle}>
          Understanding flood risk and improving emergency preparedness
        </p>
      </div>

      {sections.map((section, index) => (
        <section style={styles.card} key={index}>
          <h2 style={styles.sectionTitle}>{section.title}</h2>

          {Array.isArray(section.content) ? (
            <ul style={styles.list}>
              {section.content.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          ) : (
            <p style={styles.paragraph}>{section.content}</p>
          )}
        </section>
      ))}

      <section style={styles.card}>
        <h2 style={styles.sectionTitle}>How to Use This System</h2>
        <ul style={styles.list}>
          {usageSteps.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </section>

      <section style={styles.emergencyCard}>
        <h2 style={styles.emergencyTitle}>
          Emergency Flood Safety Guidelines
        </h2>
        <p style={styles.paragraph}>
          Follow these basic precautions during a flood emergency:
        </p>
        <ul style={styles.list}>
          {emergencyGuidelines.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
        <p style={styles.warning}>
          In an emergency, follow official local authority instructions.
          Do not depend only on this application for evacuation decisions.
        </p>
      </section>

      <section style={styles.disclaimerCard}>
        <h2 style={styles.sectionTitle}>Important Disclaimer</h2>
        <p style={styles.paragraph}>
          This application is an academic prototype that provides estimated
          flood-risk information. Predictions may contain errors and should
          not be treated as confirmed real-time flood conditions.
        </p>
        <p style={styles.paragraph}>
          Potential shelter locations require field verification. Suggested
          routes and safe zones are not guaranteed to be safe during an actual
          flood. Always follow official warnings and emergency instructions.
        </p>
      </section>

      <footer style={styles.footer}>
        <p>AI-Driven Multimodal Flood Early-Warning System</p>
        <p>Koshi Basin, Nepal</p>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    padding: "24px",
    maxWidth: "1100px",
    margin: "0 auto",
    color: "#263238",
    fontFamily: "Arial, sans-serif",
  },
  header: {
    marginBottom: "25px",
  },
  heading: {
    fontSize: "28px",
    marginBottom: "8px",
  },
  subtitle: {
    color: "#607d8b",
    fontSize: "15px",
  },
  card: {
    background: "#ffffff",
    padding: "22px",
    borderRadius: "10px",
    marginBottom: "20px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
  },
  sectionTitle: {
    fontSize: "20px",
    marginTop: 0,
    marginBottom: "14px",
    color: "#174c68",
  },
  paragraph: {
    lineHeight: "1.7",
    fontSize: "15px",
  },
  list: {
    paddingLeft: "22px",
    lineHeight: "1.9",
    fontSize: "15px",
  },
  emergencyCard: {
    background: "#fff8e8",
    borderLeft: "5px solid #d97706",
    padding: "22px",
    borderRadius: "10px",
    marginBottom: "20px",
  },
  emergencyTitle: {
    color: "#92400e",
    fontSize: "20px",
    marginTop: 0,
  },
  warning: {
    background: "#ffedd5",
    padding: "12px",
    borderRadius: "6px",
    lineHeight: "1.6",
    fontWeight: "bold",
  },
  disclaimerCard: {
    background: "#eef5f8",
    padding: "22px",
    borderRadius: "10px",
    marginBottom: "20px",
  },
  footer: {
    textAlign: "center",
    color: "#607d8b",
    padding: "15px",
    fontSize: "13px",
  },
};

export default About;
