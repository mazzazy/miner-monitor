import streamlit as st


class AppState:

    @staticmethod
    def init():

        if "selected_worker" not in st.session_state:
            st.session_state.selected_worker = None

    @staticmethod
    def set_worker(worker: str):

        st.session_state.selected_worker = worker

    @staticmethod
    def get_worker():

        return st.session_state.selected_worker