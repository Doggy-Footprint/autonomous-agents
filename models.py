# models.py
# 4단계: 스타듀밸리 세계관에 맞춘 상호작용 및 행동 로직

import datetime
import re

class World:
    """시뮬레이션 세계를 스타듀밸리 펠리칸 타운으로 정의하고 관리합니다."""
    def __init__(self, description="스타듀밸리의 펠리칸 타운"):
        self.description = description
        self.agents = {}
        # 스타듀밸리 장소로 변경
        self.locations = {
            "농장": [],
            "잡화점": [],
            "촌장의 집": [],
            "마을 광장": []
        }
        # '프로젝트 보드'를 '마을 게시판'으로 변경
        self.community_board = {
            "main_event": "아직 특별한 소식 없음"
        }
        print(f"'{self.description}' 세계가 생성되었습니다.")
        print(f"마을 게시판: {self.community_board}")

    def add_agent(self, agent, location):
        if agent.name in self.agents: return
        if location not in self.locations: return
        self.agents[agent.name] = agent
        self.locations[location].append(agent.name)
        agent.location = location
        print(f"'{agent.name}' 에이전트가 '{location}'에 추가되었습니다.")

    def get_location_state(self, location):
        if location not in self.locations: return f"'{location}'은(는) 알 수 없는 장소입니다."
        agent_names = [name for name in self.locations[location]]
        state = f"'{location}'에는 {', '.join(agent_names)}이(가) 있습니다." if agent_names else f"'{location}'에는 아무도 없습니다."
        # 현재 위치에서 마을 게시판도 볼 수 있게 함
        state += f"\n마을 게시판: {self.community_board}"
        return state

    def execute_action(self, agent, action_string):
        print(f"[{agent.name}의 행동 실행] {action_string}")
        # 스타듀밸리 행동에 맞는 정규표현식으로 변경
        move_match = re.match(r"MOVE to (.*)", action_string, re.IGNORECASE)
        say_to_match = re.match(r"SAY to (.*?): (.*)", action_string, re.IGNORECASE)
        do_match = re.match(r"DO: (.*)", action_string, re.IGNORECASE)
        post_notice_match = re.match(r"POST NOTICE: (.*)", action_string, re.IGNORECASE)
        
        observation = ""
        public_action = False

        if move_match:
            new_location = move_match.group(1).strip()
            if new_location in self.locations:
                old_location = agent.location
                if agent.name in self.locations[old_location]: self.locations[old_location].remove(agent.name)
                self.locations[new_location].append(agent.name)
                agent.location = new_location
                observation = f"{agent.name}이(가) {old_location}에서 {new_location}(으)로 이동했습니다."
                public_action = True
            else: 
                observation = f"{agent.name}이(가) {new_location}(으)로 이동하려 했지만 실패했습니다."
                agent.add_memory(observation)

        elif say_to_match:
            target_name, message = say_to_match.group(1).strip(), say_to_match.group(2).strip()
            if target_name in self.agents:
                target_agent = self.agents[target_name]
                observation = f"{agent.name}이(가) 당신에게 말합니다: \"{message}\""
                target_agent.add_memory(observation)
                agent.add_memory(f"당신이 {target_name}에게 말했습니다: \"{message}\"")
            else:
                agent.add_memory(f"{target_name}에게 말하려고 했지만, 찾을 수 없었습니다.")
        
        elif post_notice_match:
            notice = post_notice_match.group(1).strip()
            self.community_board["main_event"] = notice
            observation = f"{agent.name}이(가) 마을 게시판에 공지를 붙였습니다: \"{notice}\""
            public_action = True

        elif do_match:
            observation = f"{agent.name}이(가) {do_match.group(1).strip()}."
            public_action = True
            
        else: # 매치되는 행동이 없을 경우
            observation = f"{agent.name}이(가) 알 수 없는 행동('{action_string}')을 시도합니다."
            agent.add_memory(observation)

        if public_action:
            self.broadcast_observation(agent, observation)

    def broadcast_observation(self, acting_agent, observation):
        """공개 행동의 결과를 같은 장소의 모든 에이전트에게 전달합니다."""
        for agent in self.agents.values():
            if agent.location == acting_agent.location:
                agent.add_memory(observation)

class Agent:
    """스타듀밸리 주민처럼 행동하는 에이전트."""
    def __init__(self, name, description, llm_client, memory_db):
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.memory_db = memory_db
        self.location = None
        self.reflection_threshold = 50
        self.recent_importance_sum = 0
        self.recent_memories_for_reflection = []
        print(f"'{self.name}' 에이전트(스타듀밸리 버전)가 생성되었습니다.")

    # add_memory, _calculate_importance, reflect, perceive 메소드는 이전과 동일
    def add_memory(self, observation):
        importance_score = self._calculate_importance(observation)
        timestamp = datetime.datetime.now()
        metadata = {"timestamp": timestamp.isoformat(), "type": "observation", "importance": importance_score}
        self.memory_db.add_memory(observation, metadata)
        print(f"[{self.name}의 기억 추가 (중요도: {importance_score})] {observation}")
        self.recent_importance_sum += importance_score
        self.recent_memories_for_reflection.append(observation)
        if self.recent_importance_sum >= self.reflection_threshold: self.reflect()
    def _calculate_importance(self, memory_text):
        prompt = f"당신은 AI 에이전트의 사고 과정을 보조하는 분석 시스템입니다.\n다음 문장이 에이전트의 장기적인 목표나 행동에 얼마나 중요한지 1(일상적)에서 10(매우 중요) 사이의 정수로 평가해주세요.\n오직 숫자만 응답하세요.\n\n문장: \"{memory_text}\"\n중요도:"
        response = self.llm_client.generate_response(prompt)
        try: return int(response)
        except (ValueError, TypeError): return 3
    def reflect(self):
        print(f"\n--- [{self.name}의 성찰 시작] (누적 중요도: {self.recent_importance_sum}) ---")
        memories_str = "\n".join(self.recent_memories_for_reflection)
        prompt = f"당신은 '{self.name}' AI 에이전트입니다.\n다음은 당신의 최근 경험들입니다:\n{memories_str}\n\n이 경험들을 바탕으로 얻을 수 있는 3가지 중요한 결론이나 통찰을 요약해주세요.\n이 통찰은 당신의 미래 행동에 지침이 될 것입니다."
        reflection_text = self.llm_client.generate_response(prompt)
        metadata = {"timestamp": datetime.datetime.now().isoformat(), "type": "reflection", "importance": 10}
        self.memory_db.add_memory(f"성찰: {reflection_text}", metadata)
        print(f"[{self.name}의 성찰 완료] {reflection_text}")
        self.recent_importance_sum = 0
        self.recent_memories_for_reflection = []
        print("--- 성찰 종료 ---\n")
    def perceive(self, world):
        if not self.location: return
        location_state = world.get_location_state(self.location)
        self.add_memory(location_state)

    def plan_and_act(self, world):
        """스타듀밸리 세계관에 맞춰 행동을 결정합니다."""
        if not self.llm_client: return "DO: 가만히 있는다."
        
        current_situation = f"현재 시간은 아침입니다. 당신은 '{self.location}'에 있습니다. {world.get_location_state(self.location)}"
        retrieved_memories = self.memory_db.retrieve_memories(current_situation, n_results=5)
        memories_str = "\n".join(retrieved_memories)
        
        other_agents = [name for name in world.locations.get(self.location, []) if name != self.name]
        other_agents_str = ", ".join(other_agents) if other_agents else "없음"

        prompt = f"""
당신은 스타듀밸리 펠리칸 타운의 주민 '{self.name}'입니다. 당신의 역할은 '{self.description}'입니다.
현재 상황: {current_situation}

최근 기억 및 관련 정보:
{memories_str}

이 모든 정보를 종합하여, 당신의 역할에 가장 어울리는 단일 행동을 결정해주세요.
선택 가능한 행동 형식 (대화 가능한 대상: {other_agents_str}):
- MOVE to [장소] (이동 가능한 장소: {', '.join(world.locations.keys())})
- SAY to [대상]: [개인 메시지]
- DO: [행동 서술] (예: 밭에 물을 준다, 새로운 발명품을 구상한다, 마을을 순찰한다)
- POST NOTICE: [게시판에 쓸 내용] (당신이 촌장 Lewis일 경우)

오직 행동 문자열 하나만 응답하세요.
"""
        action = self.llm_client.generate_response(prompt)
        return action
