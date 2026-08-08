import React, { useState,useEffect } from "react";
import Navbar from "../Navbar/Navbar.jsx";
import "./ProfilePage.css"; 

const initialProfile = {
    college: "",
    course: "",
    cpi: "",
    region: "",
    name: "",
    profilePicture: "",
};

export default function ProfilePage() {
    const [profile, setProfile] = useState(initialProfile);
    const [editing, setEditing] = useState(false);
    const [form, setForm] = useState(profile);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };
    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
        const reader = new FileReader();
        reader.onload = () => {
            setForm((prev) => ({ ...prev, profilePicture: reader.result }));
        };
        reader.readAsDataURL(file);
        }
    };

    const handleEdit = () => {
        setEditing(true);
    };

    const handleSave = async() => {
        const response = await fetch("http://localhost:3000/user/profile/update", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("jwtoken")}`,
            },
            body: JSON.stringify(form),
        });
        if (!response.ok) {
            const error = await response.json();
            console.error("Error updating profile:", error);
            return;
        }
        const updatedProfile = await response.json();
        setProfile(updatedProfile);
        // setProfile(form);
        setEditing(false);
    };

    const handleCancel = () => {
        setForm(profile);
        setEditing(false);
    };

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await fetch("http://localhost:3000/user/profile", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("jwtoken")}`,
                    },
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch profile");
                }
                const data = await response.json();
                setProfile(data);
                setForm(data);
            } catch (error) {
                console.error("Error fetching profile:", error);
            }
        };
        fetchProfile();
    }, []);

    return (
        <div className="profile-container">
            <h1>Student Profile</h1>
            <div>
                <div className="profile-box profile-table">
                <div>
                {editing ? (
                   <div className="form-group">
                    <label>Profile Picture</label>
                    <input
                    type="file"
                    accept="image/*"
                    name="profilePicture"
                    onChange={handleFileChange}
                    />
                </div> 
                ) : (
                    <img
                    src={
                    form.profilePicture && form.profilePicture.trim() !== ""
                        ? form.profilePicture
                        : "https://static.vecteezy.com/system/resources/thumbnails/019/879/186/small_2x/user-icon-on-transparent-background-free-png.png"
                    }
                    alt="Profile"
                    className="profile-pic"
                    onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "https://static.vecteezy.com/system/resources/thumbnails/019/879/186/small_2x/user-icon-on-transparent-background-free-png.png";
                    }}
                    />
                )
                }
                <div>
                    <h3><strong>Student Name:</strong></h3>
                    <div>
                        {editing ? (
                            <input
                                name="name"
                                value={form.name}
                                onChange={handleChange}
                                style={{ width: "100%" }}
                                placeholder="Enter your name"
                            />
                            ) : (
                                profile.name
                            )}
                        </div>
                    </div>
                </div>
                    <div>
                        <div>
                            <h3><strong>College:</strong></h3>
                            <div>
                                {editing ? (
                                    <input
                                        name="college"
                                        value={form.college}
                                        onChange={handleChange}
                                        style={{ width: "100%" }}
                                        placeholder="Enter your college name"
                                    />
                                ) : (
                                    profile.college
                                )}
                            </div>
                        </div>
                        <div>
                            <h3><strong>Course:</strong></h3>
                            <div>
                                {editing ? (
                                    <input
                                        name="course"
                                        value={form.course}
                                        onChange={handleChange}
                                        style={{ width: "100%" }}
                                        placeholder="Enter your course name"
                                    />
                                ) : (
                                    profile.course
                                )}
                            </div>
                        </div>
                        <div>
                            <h3><strong>CPI:</strong></h3>
                            <div>
                                {editing ? (
                                    <input
                                        name="cpi"
                                        value={form.cpi}
                                        onChange={handleChange}
                                        style={{ width: "100%" }}
                                        placeholder="Enter your CPI"
                                        type="number"
                                    />
                                ) : (
                                    profile.cpi
                                )}
                            </div>
                        </div>
                        <div>
                            <h3><strong>Region:</strong></h3>
                            <div>
                                {editing ? (
                                    <input
                                        name="region"
                                        value={form.region}
                                        onChange={handleChange}
                                        style={{ width: "100%" }}
                                        placeholder="Enter your region"
                                    />
                                ) : (
                                    profile.region
                                )}
                            </div>
                        </div>
                    </div>
                    </div>
                </div>
                    {editing ? (
                        <>
                            <button onClick={handleSave} className="save-button">Save</button>
                            <button onClick={handleCancel}>Cancel</button>
                        </>
                    ) : (
                        <button onClick={handleEdit} className="edit-button" >Edit Profile</button>
                    )}
        </div>
    );
}